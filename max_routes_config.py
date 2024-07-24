config = {
    "Learning/ExternalLearning": {
        "collection": "LRN_external_learning",
        "supported_actions": [
            "add",
            "view",
            "delete",
            "update"
        ],
        "add": [
            {
                "field_name": "person_name",
                "field_value": "John Doe"
            },
            {
                "field_name": "created_at",
                "field_value": "2024-01-15T00:00:00Z"
            },
            {
                "field_name": "updated_at",
                "field_value":None
            }
        ],
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "person_name",
                    "field_value": "John Doe"
                }
            ],
            "additional_update_fields": [
                {
                    "field_name": "updated_at",
                    "field_value": "2024-01-15T00:00:00Z"
                }
            ],
            "field_in_query": [
                "learning_item_details.title","learning_item_details.topic"
            ],
            "field_not_in_update_data": [
                "learning_item_details.title", "created_at", "updated_at"
            ],
            "field_for_find_similar_documents": [
                "learning_item_details.title","learning_item_details.topic"
            ]
        },
        "view": {
            "additional_query_fields": [
                {
                    "field_name": "person_name",
                    "field_value": "John Doe"
                }
            ],
            "exclude_fields": [
                "_id",
                "person_name",
                "created_at",
                "updated_at"
            ]
        }
    },
    "Learning/NoncatalogLearning": {
        "collection": "LRN_non_catalog_learning",
        "supported_actions": [
            "add",
            "view",
            "delete",
            "update"
        ],
        "add": [
            {
                "field_name": "person_name",
                "field_value": "John Doe"
            },
            {
                "field_name": "created_at",
                "field_value": "2024-01-15T00:00:00Z"
            },
            {
                "field_name": "updated_at",
                "field_value":None
            }
        ],
        "update": {
            "additional_update_fields": [
                {
                    "field_name": "updated_at",
                    "field_value": "2024-01-15T00:00:00Z"
                }
            ],
            "field_in_query": [
                "person_name","learning_item_details.title"
            ],
            "field_not_in_update_data": [
                "person_name", "created_by", "created_at", "updated_at"
            ],
            "field_for_find_similar_documents": [
                "person_name","learning_item_details.title"
            ]
        },
        "view": {
            "additional_query_fields": [
                {
                    "field_name": "person_name",
                    "field_value": "John Doe"
                }
            ],
            "exclude_fields": [
                "_id",
                "person_name",
                "created_at",
                "updated_at"
            ]
        }
    },
    "Learning/PublishVideo": {
        "collection": "LRN_publish_video",
        "supported_actions": [
            "add",
            "view",
            "delete",
            "update"
        ],
        "update": {
            "field_in_query": [
                "video_details.title","visibility"
            ],
            "field_not_in_update_data": [
                "video_details.title"
            ],
            "field_for_find_similar_documents": [
                "video_details.title"
            ]
        }
    },
    "Learning/Community": {
        "collection": "LRN_community",
        "supported_actions": [
            "add",
            "view",
            "delete",
            "update"
        ],
        "add": [
            {
                "field_name": "created_by",
                "field_value": "John Doe"
            }
        ],
        "view": {
            "additional_query_fields": [],
            "exclude_fields": [
                "_id",
                "created_by"
            ]
        },
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "created_by",
                    "field_value": "John Doe"
                }
            ],
            "field_in_query": [
                "community_details.title"
            ],
            "field_not_in_update_data": [
                "community_details.title"
            ],
            "field_for_find_similar_documents": [
                "community_details.title"
            ]
        }
    },
    "Learning/AuthorLearning/Journey": {
        "collection": "LRN_author_learning_journey",
        "supported_actions": [
            "add",
            "view",
            "delete",
            "update"
        ],
        "add": [
            {
                "field_name": "created_by",
                "field_value": "John Doe"
            },
            {
                "field_name": "created_at",
                "field_value": "2024-01-15T00:00:00Z"
            },
            {
                "field_name": "updated_at",
                "field_value":None
            }
        ],
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "created_by",
                    "field_value": "John Doe"
                }
            ],
            "additional_update_fields": [
                {
                    "field_name": "updated_at",
                    "field_value": "2024-01-15T00:00:00Z"
                }
            ],
            "field_in_query": [
                "name","location_name","training_supplier","visible_to"
            ],
            "field_not_in_update_data": [
                "title", "created_by", "created_at", "updated_at"
            ],
            "field_for_find_similar_documents": [
                "title"
            ]
        },
        "view": {
            "additional_query_fields": [
                {
                    "field_name": "created_by",
                    "field_value": "John Doe"
                }
            ],
            "exclude_fields": [
                "_id",
                "created_by",
                "created_at",
                "updated_at"
            ]
        }
    },
    "Catalog/OnlineContent": {
        "collection": "LRN_content",
        "supported_actions": [
            "add",
            "view",
            "update",
            "delete"
        ],
        "add": [
            {
                "field_name": "type",
                "field_value": "online_content"
            },
            {
                "field_name": "status",
                "field_value": "active"
            }
        ],
        "view": {
            "additional_query_fields": [
                {
                    "field_name": "type",
                    "field_value": "online_content"
                }
            ],
            "exclude_fields": [
                "_id",
                "type",
                "status"
            ]
        },
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "type",
                    "field_value": "online_content"
                }
            ],
            "field_in_query": [
                "title"
            ],
            "field_not_in_update_data": [
                "title", "type", "status"
            ],
            "field_for_find_similar_documents": [
                "title"
            ]
        }
    },
    "Catalog/Video": {
        "collection": "LRN_content",
        "supported_actions": [
            "add",
            "view",
            "update",
            "delete"
        ],
        "add": [
            {
                "field_name": "type",
                "field_value": "video"
            },
            {
                "field_name": "status",
                "field_value": "active"
            }
        ],
        "view": {
            "additional_query_fields": [
                {
                    "field_name": "type",
                    "field_value": "video"
                }
            ],
            "exclude_fields": [
                "_id",
                "type",
                "status"
            ]
        },
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "type",
                    "field_value": "video"
                }
            ],
            "field_in_query": [
                "title"
            ],
            "field_not_in_update_data": [
                "title", "type", "status"
            ],
            "field_for_find_similar_documents": [
                "title"
            ]
        }
    },
    "Catalog/WebLink": {
        "collection": "LRN_content",
        "supported_actions": [
            "add",
            "view",
            "update",
            "delete"
        ],
        "add": [
            {
                "field_name": "type",
                "field_value": "web_link"
            }
        ],
        "view": {
            "additional_query_fields": [
                {
                    "field_name": "type",
                    "field_value": "web_link"
                }
            ],
            "exclude_fields": [
                "_id",
                "type"
            ]
        },
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "type",
                    "field_value": "weblink"
                }
            ],
            "field_in_query": [
                "title"
            ],
            "field_not_in_update_data": [
                "title", "type"
            ],
            "field_for_find_similar_documents": [
                "title"
            ]
        }
    },
    "Catalog/PdfFile": {
        "collection": "LRN_content",
        "supported_actions": [
            "add",
            "view",
            "update",
            "delete"
        ],
        "add": [
            {
                "field_name": "type",
                "field_value": "pdf_file"
            },
            {
                "field_name": "status",
                "field_value": "active"
            }
        ],
        "view": {
            "additional_query_fields": [
                {
                    "field_name": "type",
                    "field_value": "pdf_file"
                }
            ],
            "exclude_fields": [
                "_id",
                "type",
                "status"
            ]
        },
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "type",
                    "field_value": "pdf_file"
                }
            ],
            "field_in_query": [
                "title"
            ],
            "field_not_in_update_data": [
                "title", "type", "status"
            ],
            "field_for_find_similar_documents": [
                "title"
            ]
        }
    },
    "Catalog/CoverArt": {
        "collection": "LRN_content",
        "supported_actions": [
            "add",
            "view",
            "update",
            "delete"
        ],
        "add": [
            {
                "field_name": "type",
                "field_value": "cover_art"
            },
            {
                "field_name": "status",
                "field_value": "active"
            }
        ],
        "view": {
            "additional_query_fields": [
                {
                    "field_name": "type",
                    "field_value": "cover_art"
                }
            ],
            "exclude_fields": [
                "_id",
                "type",
                "status"
            ]
        },
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "type",
                    "field_value": "cover_art"
                }
            ],
            "field_in_query": [
                "title"
            ],
            "field_not_in_update_data": [
                "title", "type", "status"
            ],
            "field_for_find_similar_documents": [
                "title"
            ]
        }
    },
    "Catalog/Assessment": {
        "collection": "LRN_assessment",
        "supported_actions": [
            "add",
            "view",
            "update",
            "delete"
        ],
        "update": {
            "field_in_query": [
                "title","status"
            ],
            "field_not_in_update_data": [
                "title"
            ],
            "field_for_find_similar_documents": [
                "title"
            ]
        }
    },
    "Catalog/ObservationChecklist": {
        "collection": "LRN_observation_list",
        "supported_actions": [
            "add",
            "view",
            "update",
            "delete"
        ],
        "update": {
            "field_in_query": [
                "tile","status","observer_type"
            ],
            "field_not_in_update_data": [
                "title", "observer_type"
            ],
            "field_for_find_similar_documents": [
                "title", "observer_type"
            ]
        }
    },
    "Catalog/Location": {
        "collection": "LRN_location",
        "supported_actions": [
            "add",
            "view",
            "update",
            "delete"
        ],
        "update": {
            "field_in_query": [
                "name"
            ],
            "field_not_in_update_data": [
                "name","city","state","country","zip_code"
            ],
            "field_for_find_similar_documents": [
                "name","city","state","country"
            ]
        }
    },
    "Catalog/Classroom": {
        "collection": "LRN_classroom",
        "supported_actions": [
            "add",
            "view",
            "update",
            "delete"
        ],
        "add": [
            {
                "field_name": "created_by",
                "field_value": "John Doe"
            },
            {
                "field_name": "created_at",
                "field_value": "2024-01-15T00:00:00Z"
            },
            {
                "field_name": "updated_at",
                "field_value":None
            }
        ],
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "created_by",
                    "field_value": "John Doe"
                }
            ],
            "additional_update_fields": [
                {
                    "field_name": "updated_at",
                    "field_value": "2024-01-15T00:00:00Z"
                }
            ],
            "field_in_query": [
                "name","location_name","training_supplier","visible_to"
            ],
            "field_not_in_update_data": [
                "name", "created_by", "created_at", "updated_at"
            ],
            "field_for_find_similar_documents": [
                "name"
            ]
        },
        "view": {
            "additional_query_fields": [
                {
                    "field_name": "created_by",
                    "field_value": "John Doe"
                }
            ],
            "exclude_fields": [
                "_id",
                "created_by",
                "created_at",
                "updated_at"
            ]
        }
    },
    "Catalog/Instructor": {
        "collection": "LRN_instructor",
        "supported_actions": [
            "add",
            "view",
            "delete",
            "update"
        ],
        "update": {
            "field_in_query": [
                "name","department","job","business_unit"
            ],
            "field_not_in_update_data": [
                "name", "person_number"
            ],
            "field_for_find_similar_documents": [
                "name", "department", "job", "business_unit"
            ]
        }
    },
    "Catalog/TrainingSupplier": {
        "collection": "LRN_training_supplier",
        "supported_actions": [
            "add",
            "view",
            "update",
            "delete"
        ],
        "update": {
            "field_in_query": [
                "name","contact","context_segment","visible_to"
            ],
            "field_not_in_update_data": [
                "name"
            ],
            "field_for_find_similar_documents": [
                "name", "contact", "context_segment"
            ]
        }
    },
    "Course/Offering":{
        "collection": "LRN_course_offering",
        "supported_actions" :["add","view","update","delete"],
        "add": [
            {
                "field_name": "metadata.created_by",
                "field_value": "John Doe"
            },
            {
                "field_name": "metadata.last_updated_by",
                "field_value": None
            },
            {
                "field_name": "metadata.creation_date",
                "field_value":"2024-07-01 10:00:00"
            },
            {
                "field_name": "metadata.last_update_date",
                "field_value":None
            }
        ],
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "metadata.created_by",
                    "field_value": "John Doe"
                }
            ],
            "additional_update_fields": [
                {
                    "field_name": "metadata.last_updated_by",
                    "field_value": "John Doe"
                },
                {
                    "field_name": "metadata.last_update_date",
                    "field_value": "2024-01-15T00:00:00Z"
                }
            ],
            "field_in_query": [
                "general_information.basic_information.title"
            ],
            "field_not_in_update_data": [
                "general_information.basic_information.title"
            ],
            "field_for_find_similar_documents": [
                "general_information.basic_information.title"
            ]
        },
        "view": {
            "exclude_fields": [
                "_id",
                "metadata.creation_date",
                "metadata.created_by",
                "metadata.last_update_date",
                "metadata.last_updated_by"
            ]
        }
    },
    "Course":{
        "collection": "LRN_course",
        "supported_actions" :["add","view","update","delete"],
        "add": [
            {
                "field_name": "created_by",
                "field_value": "John Doe"
            },
            {
                "field_name": "course_number",
                "field_value": "DA202"
            },
            {
                "field_name": "timestamps.created_at",
                "field_value":"2024-07-01 10:00:00"
            },
            {
                "field_name": "timestamps.updated_at",
                "field_value":None
            }
        ],
        "update": {
            "additional_query_fields": [
                {
                    "field_name": "metadata.created_by",
                    "field_value": "John Doe"
                }
            ],
            "additional_update_fields": [
                {
                    "field_name": "created_by",
                    "field_value": "John Doe"
                },
                {
                    "field_name": "course_number",
                    "field_value": "DA202"
                }
            ],
            "field_in_query": [
                "general_information.basic_information.title"
            ],
            "field_not_in_update_data": [
                "general_information.basic_information.title"
            ],
            "field_for_find_similar_documents": [
                "general_information.basic_information.title"
            ]
        },
        "view": {
            "exclude_fields": [
                "_id",
                "timestamps.created_at"
                "timestamps.updated_at",
                "created_by"
            ]
        }
    },
    
    "JourneyManagement/ManageJourney": {
        "collection": "JRN_journey",
        "supported_actions": ["add", "update", "delete", "view", "search"],
        "add": [
            {
                "field_name": "created_at",
                "field_value": "2024-01-15T00:00:00Z"
            },
            {
                "field_name": "updated_at",
                "field_value": None
            }
        ],
        "update": {
            "additional_update_fields": [
                {
                    "field_name": "updated_at",
                    "field_value": "2024-01-15T00:00:00Z"
                }
            ],
            "field_in_query": ["name"],
            "field_not_in_update_data": ["created_at"],
            "field_for_find_similar_documents": ["name"]
        },
        "view": {
            "additional_query_fields": [],
            "exclude_fields": ["_id"]
        },
        "search": {
            "additional_query_fields": [],
            "exclude_fields": ["_id"]
        }
    },
    "JourneyManagement/GenerateReports": {
        "collection": "JRN_journey",
        "supported_actions": ["generate_report"]
    },
    "processHrInfoUK": {
        "collection": "HRM_employee_details",
        "supported_actions": [
            "add"
        ]
    }
}

# "Catalog/OnlineContent   last route
# Assign Learning
# supported_actions = ['add', 'create', 'search', 'view', 'update', 'edit', 'delete', 'export']