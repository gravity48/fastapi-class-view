import functools
import inspect
from inspect import Parameter
from types import FunctionType
from typing import Callable, List, _GenericAlias

from fastapi import Depends
from pydantic import BaseModel, create_model

from .type import PyModel, SlugField, UserModel


def change_annotation(annotation, return_type=None, slug=None):
    if annotation is PyModel:
        assert return_type is not None, 'no py_model attr'
        return return_type
    elif annotation is SlugField:
        assert slug is not None, 'no slug attr'
        return slug
    elif isinstance(annotation, _GenericAlias):
        args = getattr(annotation, '__args__')
        origin = getattr(annotation, '__origin__')
        new_args = tuple(map(lambda x: change_annotation(x, return_type, slug), args))
        return _GenericAlias(origin, new_args, inst=False, name=origin.__name__)
    else:
        return annotation


def class_annotation(annotation, return_type=None, slug=None):
    if issubclass(annotation, BaseModel):
        fields = {}
        for key, value in annotation.model_fields.items():
            value.annotation = change_annotation(value.annotation, return_type, slug)
            fields[key] = (value.annotation, value.default)
        return create_model(
            'ResponseModel',
            **fields,
            __base__=annotation,
        )
    else:
        return annotation


class DynamicParamMeta(type):
    def __new__(cls, name, bases, attrs):
        if name == 'APIView':
            return super().__new__(cls, name, bases, attrs)
        assert 'py_model' in attrs, 'View not implemented py_models attr'
        assert 'permissions' in attrs, 'View not implemented permissions attr'
        py_model = attrs['py_model']
        perm = attrs['permissions']
        slug_field = attrs.get('slug_field_type')
        for base in bases:
            for attr_name, attr_value in base.__dict__.items():
                if inspect.isfunction(attr_value) and attr_name not in attrs:
                    attrs[attr_name] = cls.deepcopy_func(attr_value)
        for attr_name, attr_value in attrs.items():
            if inspect.isfunction(attr_value):
                attrs[attr_name] = cls.wrap_method(
                    attr_value,
                    return_type=py_model[attr_name],
                    perm=perm[attr_name],
                    slug_field=slug_field,
                )
        return super().__new__(cls, name, (), attrs)

    @staticmethod
    def deepcopy_func(f) -> Callable:
        g = FunctionType(
            f.__code__,
            f.__globals__,
            name=f.__name__,
            argdefs=f.__defaults__,
            closure=f.__closure__,
        )
        g = functools.update_wrapper(g, f)
        g.__kwdefaults__ = f.__kwdefaults__
        return g

    @staticmethod
    def wrap_method(method, return_type=None, perm=None, slug_field=None):
        sig = inspect.signature(method)
        req_parameters: List[Parameter] = []
        def_parameters: List[Parameter] = []
        for name in sig.parameters:
            parameter = sig.parameters[name]
            annotation = change_annotation(parameter.annotation, return_type, slug_field)
            parameter = parameter.replace(annotation=annotation)
            if parameter.annotation is UserModel:
                parameter = parameter.replace(default=Depends(perm))
            if parameter.default is Parameter.empty:
                req_parameters.append(parameter)
            else:
                def_parameters.append(parameter)

        parameters = req_parameters + def_parameters
        return_annotation = sig.return_annotation

        if inspect.isclass(return_annotation):
            return_annotation = class_annotation(return_annotation, return_type)
        else:
            return_annotation = change_annotation(return_annotation, return_type)

        sig = sig.replace(parameters=parameters, return_annotation=return_annotation)

        method.__signature__ = sig

        return method
