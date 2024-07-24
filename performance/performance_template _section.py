from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# MongoDB configuration
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client.PCL_Interns
collection = db.P_PerformanceTemplateSections

@app.route('/add_performance_template_section', methods=['POST'])
def add_template_section():
    data = request.get_json()
    
    # Insert new template section into the database
    new_template_section = {
        "name": data.get('name'),
        "description": data.get('description'),
        "comments": data.get('comments'),
        "from_date": datetime.datetime.strptime(data.get('from_date'), "%Y-%m-%dT%H:%M:%S.%fZ"),
        "to_date": datetime.datetime.strptime(data.get('to_date'), "%Y-%m-%dT%H:%M:%S.%fZ"),
        "status": data.get('status'),
        "section_processing": {
            "section_type": data.get('section_type'),
            "competencies_section_name": data.get('competencies_section_name'),
            "ratings": {
                "section_rating_model": data.get('section_rating_model'),
                "rating_calculations": {
                    "calculation_rule_for_section": data.get('calculation_rule_for_section'),
                    "decimal_places": data.get('decimal_places'),
                    "mapping_metric": data.get('mapping_metric'),
                    "fast_formula_rule": data.get('fast_formula_rule'),
                    "decimal_rounding_rule": data.get('decimal_rounding_rule'),
                    "mapping_method": data.get('mapping_method')
                },
                "enable_manual_section_rating": data.get('enable_manual_section_rating', False),
                "require_manager_justification_if_manual_and_calculated_ratings_are_different": data.get('require_manager_justification_if_manual_and_calculated_ratings_are_different', False)
            },
            "comments": {
                "enable_section_comments": data.get('enable_section_comments', False)
            },
            "weighting": {
                "weight_section": data.get('weight_section', False),
                "section_weight": data.get('section_weight'),
                "section_minimum_weight": data.get('section_minimum_weight')
            }
        },
        "item_processing": {
            "enable_items": data.get('enable_items', False),
            "ratings_and_calculations": {
                "rate_items": data.get('rate_items', False),
                "rating_type": data.get('rating_type'),
                "use_section_rating_model_for_performance_rating": data.get('use_section_rating_model_for_performance_rating', False),
                "performance_rating_model": data.get('performance_rating_model'),
                "item_calculation": data.get('item_calculation')
            },
            "comments": {
                "enable_item_comments": data.get('enable_item_comments', False)
            },
            "properties": {
                "minimum_weight": data.get('minimum_weight', False),
                "weight": data.get('weight', False),
                "required": data.get('required', False)
            }
        },
        "section_content": {
            "populate_with_competencies_using_profile": data.get('populate_with_competencies_using_profile', False),
            "profile_type": data.get('profile_type'),
            "use_specific_content_items": data.get('use_specific_content_items', False),
            "content_items": data.get('content_items', [])
        }
    }

    result = collection.insert_one(new_template_section)
    return jsonify({"message": "Template section added", "id": str(result.inserted_id)}), 201

@app.route('/update_performance_template_section', methods=['POST'])
def update_template_section():
    data = request.get_json()
    
    # Update template section in the database
    updated_template_section = {
        "description": data.get('description'),
        "comments": data.get('comments'),
        "from_date": datetime.datetime.strptime(data.get('from_date'), "%Y-%m-%dT%H:%M:%S.%fZ"),
        "to_date": datetime.datetime.strptime(data.get('to_date'), "%Y-%m-%dT%H:%M:%S.%fZ"),
        "status": data.get('status'),
        "section_processing": {
            "section_type": data.get('section_type'),
            "competencies_section_name": data.get('competencies_section_name'),
            "ratings": {
                "section_rating_model": data.get('section_rating_model'),
                "rating_calculations": {
                    "calculation_rule_for_section": data.get('calculation_rule_for_section'),
                    "decimal_places": data.get('decimal_places'),
                    "mapping_metric": data.get('mapping_metric'),
                    "fast_formula_rule": data.get('fast_formula_rule'),
                    "decimal_rounding_rule": data.get('decimal_rounding_rule'),
                    "mapping_method": data.get('mapping_method')
                },
                "enable_manual_section_rating": data.get('enable_manual_section_rating', False),
                "require_manager_justification_if_manual_and_calculated_ratings_are_different": data.get('require_manager_justification_if_manual_and_calculated_ratings_are_different', False)
            },
            "comments": {
                "enable_section_comments": data.get('enable_section_comments', False)
            },
            "weighting": {
                "weight_section": data.get('weight_section', False),
                "section_weight": data.get('section_weight'),
                "section_minimum_weight": data.get('section_minimum_weight')
            }
        },
        "item_processing": {
            "enable_items": data.get('enable_items', False),
            "ratings_and_calculations": {
                "rate_items": data.get('rate_items', False),
                "rating_type": data.get('rating_type'),
                "use_section_rating_model_for_performance_rating": data.get('use_section_rating_model_for_performance_rating', False),
                "performance_rating_model": data.get('performance_rating_model'),
                "item_calculation": data.get('item_calculation')
            },
            "comments": {
                "enable_item_comments": data.get('enable_item_comments', False)
            },
            "properties": {
                "minimum_weight": data.get('minimum_weight', False),
                "weight": data.get('weight', False),
                "required": data.get('required', False)
            }
        },
        "section_content": {
            "populate_with_competencies_using_profile": data.get('populate_with_competencies_using_profile', False),
            "profile_type": data.get('profile_type'),
            "use_specific_content_items": data.get('use_specific_content_items', False),
            "content_items": data.get('content_items', [])
        }
    }

    result = collection.update_one({"name": data.get('name')}, {"$set": updated_template_section})
    if result.matched_count > 0:
        return jsonify({"message": "Template section updated"}), 200
    else:
        return jsonify({"message": "Template section not found"}), 404

@app.route('/get_performance_template_section', methods=['POST'])
def get_template_section():
    data = request.get_json()
    name = data.get('name')
    template_section = collection.find_one({"name": name})

    if template_section:
        template_section['_id'] = str(template_section['_id'])
        template_section['from_date'] = template_section['from_date'].isoformat() + 'Z'
        template_section['to_date'] = template_section['to_date'].isoformat() + 'Z'
        return jsonify(template_section)
    else:
        return jsonify({"message": "Template section not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
