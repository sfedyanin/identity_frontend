import logging
from string import Formatter
from django.conf import settings

_frmtr = Formatter()
logger = logging.getLogger('vdx_id.%s' % __name__)


class MissingArgException(Exception):
    pass


def resolve_param_string(pstring, object_arr):
    """Given a parameterized string, and object array,
        generate a complete string using properties/attributes from objs"""
    
    def _extract_keywords(pstr):
        string_parts = _frmtr.parse(pstr)
        fieldnames = [
            fname for _, fname, _, _ in string_parts if fname]
        return fieldnames

    variables = _extract_keywords(pstring)
    arg_dict = {v: None for v in variables}
    fulfil_args_from_objects(arg_dict, object_arr)
    return pstring.format(**arg_dict)


def fulfil_args_from_objects(arg_dict, object_arr,
        raise_if_missing=True, override_existing_vals=False,
        recurse_into_referenced_args=True, recurse_count=0, recurse_limit=5):
    """Retrieves args in arg_dict.keys from objects in object_arr.
    Can optionally raise an exception if args not satisfied (default:true).
    Can override existing values as it searches through Objs (default:false).
    Recurses into objects if values match a regex defined in
        settings.ATTRIBUTE_REGEX
    """
    logger.debug("Retrieving args %s from Objs: %s" % (arg_dict, object_arr))
    
    _resolve_params_from_objs(arg_dict, object_arr, override_existing_vals)

    # Maybe raise an exception if any args missing
    if raise_if_missing and None in arg_dict.values():
        missing_args = list(
            arg for arg, val in arg_dict.items()
            if val is None)
        raise MissingArgException(
            "Args(%s) not satisfied in Objs %s"
            % (missing_args, object_arr))
    
    # TODO: Review what is possible using best practices;
    #       https://realpython.com/python-string-formatting/
    if recurse_into_referenced_args:
        if recurse_count > recurse_limit:
            raise Exception("Arg recursion exceeds limit (%s)" % recurse_limit)
        
        inf_key_list, inf_arg_dict = extract_inferred_keys(arg_dict)
        if len(inf_key_list) > 0:
            # ReCall this function with the inferred arg_dict
            fulfil_args_from_objects(
                inf_arg_dict, object_arr,
                raise_if_missing=raise_if_missing,
                override_existing_vals=override_existing_vals,
                recurse_count=recurse_count+1)
            # Resolve the original arg_dict with found arguments
            for key in inf_key_list:
                satified_str = arg_dict[key].format(**inf_arg_dict)
                if satified_str:
                    arg_dict[key] = satified_str


def extract_inferred_keys(arg_dict):
    """Extracts inferred key info from dict.
    A list is returned for all keys requiring inferred values.
    A dict is returned of {key: None} for each key."""
    inf_key_list = [] # Records keys which infer other args in value
    inf_arg_dict = {} # A new arg_dict for inferred args
    for k, v in arg_dict.items():
        logger.debug("Checking inferred in '%s'" % str(v))
        match = settings.ATTRIBUTE_REGEX.match(str(v))
        if match:
            found_groups = set(match.groups())
            # Store this key as needing inferred value
            inf_key_list.append(k)
            # Enter each of the parameters to the inf arg dict
            for inferred_key in found_groups:
                inf_arg_dict[inferred_key] = None
    if len(inf_key_list) > 0:
        logger.debug("Found inferred arguments: %s" % inf_key_list)
    return inf_key_list, inf_arg_dict


def _resolve_params_from_objs(arg_dict, object_arr, override_existing_vals):

    # Internal function to return arg immediately when found
    def __resolve_param_in_obj(param, obj):
        # If this obj is a dictionary and has they key, grab that
        if type(obj) == dict and param in obj.keys():
            if obj[param] is not None:
                return obj[param]
        # Iterate through task_parameter generator if available
        if hasattr(obj, 'task_parameters'):
            for obj_params in obj.task_parameters:
                val = obj_params.get(param)
                if val is not None:
                    return val
        # Otherwise try get it via attribute
        if hasattr(obj, param):
            val = getattr(obj, param)
            if val is not None:
                return val
        
    # For each object in the list given
    for obj in object_arr:
        # For each argument that we need to satisfy
        for k in arg_dict.keys():
            # Skip if we have already satisfied this argument (not overriding)
            if not override_existing_vals and arg_dict[k] is not None:
                continue
            val = __resolve_param_in_obj(k, obj)
            if val:
                arg_dict[k] = val
    