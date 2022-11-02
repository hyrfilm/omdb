from backend import api, wsgi, test, swagger
from backend.wsgi import messages, message_types


class NestedResponse(messages.Message):
    test = messages.BooleanField(1)


class TestResponse(messages.Message):
    id = messages.StringField(1, required=True)
    value = messages.IntegerField(2)
    nested = messages.MessageField(NestedResponse, 3, repeated=True)


@api.service("swagger")
class Swagger(wsgi.Service):
    @swagger.swagger("Test method")
    @wsgi.method(message_types.VoidMessage, TestResponse)
    def test(self, request):
        return TestResponse(id="test")


@api.service("swagger2")
class Swagger2(wsgi.Service):
    @swagger.swagger("Test method")
    @wsgi.method(message_types.VoidMessage, TestResponse)
    def test(self, request):
        return TestResponse(id="test")


@api.service("swagger3")
class Swagger3(wsgi.Service):
    @swagger.swagger("Test method", deprecated_fields=[TestResponse.value])
    @wsgi.method(message_types.VoidMessage, TestResponse)
    def test(self, request):
        return TestResponse(id="test")


class TestSwagger(test.TestCase):

    def test_message_to_schema(self):
        self.assertEqual(swagger.message_to_schema(TestResponse), {
            'properties': {
                'id': {
                    'type': 'string'
                },
                'nested': {
                    'items': {
                        'properties': {
                            'test': {
                                'type': 'boolean'
                            }
                        },
                        'type': 'object'
                    },
                    'type': 'array'
                },
                'value': {
                    'type': 'integer'
                }
            },
            'required': ['id'],
            'type': 'object'
        })
        self.assertEqual(swagger.message_to_schema(message_types.VoidMessage), {
            'type': 'object'
        })

    def test_service_to_definition(self):
        self.assertEqual(swagger.service_to_definition(Swagger2), {
            'info': {
                'version': '',
                'description': '',
                'title': ''
            },
            'paths': {
                '.test': {
                    'post': {
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'schema': {
                                    'properties': {
                                        'id': {
                                            'type': 'string'
                                        },
                                        'nested': {
                                            'items': {
                                                'properties': {
                                                    'test': {
                                                        'type': 'boolean'
                                                    }
                                                },
                                                'type': 'object'
                                            },
                                            'type': 'array'
                                        },
                                        'value': {
                                            'type': 'integer'
                                        }
                                    },
                                    'required': ['id'],
                                    'type': 'object'
                                }
                            },
                            '400': {
                                'description': 'Bad Request',
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'error_name': {
                                            'type': 'string'
                                        },
                                        'error_message': {
                                            'type': 'string'
                                        },
                                        'state': {
                                            'type': 'string'
                                        }
                                    }
                                }
                            }
                        },
                        'parameters': [{
                            'schema': {
                                'type': 'object'
                            },
                            'name': '',
                            'in': 'body'
                        }],
                        'produces': ['application/json'],
                        'summary': 'Test method',
                        'consumes': ['application/json'],
                        'description': ''
                    }
                }
            },
            'schemes': ['https'],
            'tags': [],
            'basePath': '/api/swagger2',
            'securityDefinitions': {
                'Bearer': {
                    'type': 'apiKey',
                    'name': 'Authorization',
                    'in': 'header'
                }
            },
            'host': None,
            'swagger': '2.0'
        })
        self.assertEqual(swagger.service_to_definition(Swagger3), {
            'info': {
                'version': '',
                'description': '',
                'title': ''
            },
            'paths': {
                '.test': {
                    'post': {
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'schema': {
                                    'properties': {
                                        'id': {
                                            'type': 'string'
                                        },
                                        'nested': {
                                            'items': {
                                                'properties': {
                                                    'test': {
                                                        'type': 'boolean'
                                                    }
                                                },
                                                'type': 'object'
                                            },
                                            'type': 'array'
                                        }
                                    },
                                    'required': ['id'],
                                    'type': 'object'
                                }
                            },
                            '400': {
                                'description': 'Bad Request',
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'error_name': {
                                            'type': 'string'
                                        },
                                        'error_message': {
                                            'type': 'string'
                                        },
                                        'state': {
                                            'type': 'string'
                                        }
                                    }
                                }
                            }
                        },
                        'parameters': [{
                            'schema': {
                                'type': 'object'
                            },
                            'name': '',
                            'in': 'body'
                        }],
                        'produces': ['application/json'],
                        'summary': 'Test method',
                        'consumes': ['application/json'],
                        'description': ''
                    }
                }
            },
            'schemes': ['https'],
            'tags': [],
            'basePath': '/api/swagger3',
            'securityDefinitions': {
                'Bearer': {
                    'type': 'apiKey',
                    'name': 'Authorization',
                    'in': 'header'
                }
            },
            'host': None,
            'swagger': '2.0'
        })
