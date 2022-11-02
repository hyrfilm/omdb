from backend.wsgi import messages


def swagger(summary="", deprecated_fields=[]):
    def decorator(f):
        f.swagger = True
        f.summary = summary
        f.deprecated_fields = deprecated_fields
        return f
    return decorator


def variant_to_type(variant):
    mapping = {
        "DOUBLE": "number",
        "FLOAT": "number",
        "INT64": "integer",
        "UINT64": "integer",
        "INT32": "integer",
        "BOOL": "boolean",
        "STRING": "string",
        "MESSAGE": "null",
        "BYTES": "null",
        "UINT32": "integer",
        "ENUM": "null",
        "SINT32": "integer",
        "SINT32": "integer"
    }
    return mapping.get(variant.name, "null")


def message_to_schema(message, deprecated_fields=[]):
    schema = {
        "type": "object"
    }

    properties = {}
    required = []

    for field in message._Message__by_number.values():
        if field not in deprecated_fields:
            if isinstance(field, messages.MessageField):
                if field.repeated:
                    properties[field.name] = {
                        "type": "array",
                        "items": message_to_schema(field._MessageField__type, deprecated_fields)
                    }
                else:
                    properties[field.name] = {
                        "type": "object",
                        "schema": message_to_schema(field._MessageField__type, deprecated_fields)
                    }
            else:
                if field.repeated:
                    properties[field.name] = {
                        "type": "array",
                        "items": {
                            "type": variant_to_type(field.variant)
                        }
                    }
                else:
                    properties[field.name] = {
                        "type": variant_to_type(field.variant)
                    }
            if field.required:
                required.append(field.name)

    if len(properties.values()):
        schema["properties"] = properties
    if len(required):
        schema["required"] = required

    return schema


def service_to_definition(service):
    definition = dict(
        host=None,
        basePath=service.path,
        schemes=["https"],
        info=dict(title=service.title, version="", description="%s" % (service.__doc__ or "")),
        paths=dict(),
        swagger="2.0",
        tags=[],
        securityDefinitions=dict(
            Bearer={
                "type": "apiKey",
                "name": "Authorization",
                "in": "header"
            }
        )
    )

    for path, f in service._ServiceClass__remote_methods.items():
        if hasattr(f, "swagger"):
            p = ".%s" % path
            definition["paths"][p] = {
                "post": {
                    "summary": f.summary,
                    "description": "%s" % (f.remote._RemoteMethodInfo__method.__doc__ or ""),
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "in": "body",
                        "name": "",
                        "schema": message_to_schema(f.remote._RemoteMethodInfo__request_type, f.deprecated_fields)
                    }],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "schema": message_to_schema(f.remote._RemoteMethodInfo__response_type, f.deprecated_fields)
                        },
                        "400": {
                            "description": "Bad Request",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error_message": {
                                        "type": "string"
                                    },
                                    "error_name": {
                                        "type": "string"
                                    },
                                    "state": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if hasattr(f, "oauth2_required"):
                definition["paths"][p]["post"]["security"] = [dict(Bearer=[])]
                definition["paths"][p]["post"]["responses"]["401"] = {
                    "description": "Unauthorized",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error_message": {
                                "type": "string"
                            },
                            "error_name": {
                                "type": "string"
                            },
                            "state": {
                                "type": "string"
                            }
                        }
                    }
                }
            elif hasattr(f, "oauth2_optional"):
                definition["paths"][p]["post"]["security"] = [dict(), dict(Bearer=[])]

    return definition
