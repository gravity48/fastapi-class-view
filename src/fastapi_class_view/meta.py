import inspect
from inspect import Parameter
from types import MappingProxyType
from typing import Callable, Dict, List, _GenericAlias

from fastapi import Depends
from pydantic import BaseModel, create_model

from .type import PyModel, SlugField, UserModel


class DynamicParamMeta(type):
    def __new__(cls, name, bases, attrs):
        if name == 'APIView':
            return super().__new__(cls, name, bases, attrs)
        assert 'py_model' in attrs, 'View not implemented py_models attr'
        assert 'permissions' in attrs, 'View not implemented permissions attr'
        py_model = attrs['py_model']
        perm = attrs['permissions']
        slug_field = attrs.get('slug_field_type')
        cls.wrapper_methods(attrs, py_model, perm, slug_field, cls.wrap_method)
        for base in bases:
            cls.wrapper_methods(base.__dict__, py_model, perm, slug_field, cls.wrap_method, base)
        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def wrapper_methods(
        attrs: Dict | MappingProxyType,
        py_model: Dict,
        permissions: Dict,
        slug_field: SlugField,
        wrap_method: Callable,
        obj_=None,
    ):
        for attr_name, attr_value in attrs.items():
            if (
                callable(attr_value)
                and attr_name != "__init__"
                and attr_name != 'service'
                and attr_name != 'slug_field_type'
            ):
                if isinstance(attrs, Dict):
                    attrs[attr_name] = wrap_method(
                        attr_value,
                        return_type=py_model[attr_name],
                        perm=permissions[attr_name],
                        slug_field=slug_field,
                    )
                else:
                    setattr(
                        obj_,
                        attr_name,
                        wrap_method(
                            attr_value,
                            return_type=py_model[attr_name],
                            perm=permissions[attr_name],
                            slug_field=slug_field,
                        ),
                    )

    @staticmethod
    def wrap_method(method, return_type=None, perm=None, slug_field=None):
        sig = inspect.signature(method)
        parameters: List[Parameter] = []
        for name in sig.parameters:
            if sig.parameters[name].annotation is PyModel:
                assert return_type is not None, 'no py_model attr'
                parameters.append(
                    sig.parameters[name].replace(
                        annotation=return_type,
                    ),
                )
            elif sig.parameters[name].annotation is UserModel:
                assert perm is not None, 'no permissions attr'
                parameters.append(sig.parameters[name].replace(default=Depends(perm)))
            elif sig.parameters[name].annotation is SlugField:
                assert slug_field is not None, 'no slug field attr'
                parameters.append(sig.parameters[name].replace(annotation=slug_field))
            else:
                parameters.append(sig.parameters[name])

        parameters.sort(key=lambda x: 1 if x.default is Parameter.empty else 2)

        return_annotation = sig.return_annotation
        if inspect.isclass(return_annotation):
            if issubclass(return_annotation, BaseModel):
                fields = {}
                for key, value in return_annotation.model_fields.items():
                    if value.annotation is PyModel:
                        value.annotation = return_type
                    if isinstance(value.annotation, _GenericAlias):
                        args = getattr(value.annotation, '__args__')
                        new_args = tuple(map(lambda x: return_type if x is PyModel else x, args))
                        setattr(value.annotation, '__args__', new_args)
                    fields[key] = (value.annotation, value.default)
                return_annotation = create_model(
                    'ResponseModel',
                    **fields,
                    __base__=return_annotation,
                )
        else:
            if return_annotation is PyModel:
                return_annotation = return_type
            elif isinstance(return_annotation, _GenericAlias):
                args = getattr(return_annotation, '__args__')
                new_args = tuple(map(lambda x: return_type if x is PyModel else x, args))
                setattr(return_annotation, '__args__', new_args)

        sig = sig.replace(parameters=parameters, return_annotation=return_annotation)

        method.__annotations__['return'] = return_annotation
        method.__signature__ = sig

        return method
