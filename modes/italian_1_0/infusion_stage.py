import json

def get_infusion_stage(parameters: json, start_node: int, end_node: int):
    
    infusion_stage =   {
        "name": "infusion",
        "nodes": [
            {
                "id": start_node,
                "controllers": [
                 {
                  "kind": "time_reference",
                  "id": 4
                 }
                ],
                "triggers": [
                 {
                  "kind": "exit",
                  "next_node_id": 13
                 }
                ]
            },
            {
             "id": 13,
             "controllers": [
              {
               "kind": "temperature_controller",
               "algorithm": "Cylinder Temperature PID v1.0",
               "curve": {
                "id": 12,
                "interpolation_kind": "linear_interpolation",
                "points": [
                 [
                  0,
                  25
                 ]
                ],
                "time_reference_id": 4
               }
              },
              {
               "kind": "pressure_controller",
               "algorithm": "Pressure PID v1.0",
               "curve": {
                "id": 7,
                "interpolation_kind": "catmull_interpolation",
                "points": [
                 [
                  0,
                  8
                 ]
                ],
                "time_reference_id": 4
               }
              },
              {
               "kind": "position_reference",
               "id": 1
              }
             ],
             "triggers": [
              {
               "kind": "timer_trigger",
               "timer_reference_id": 4,
               "operator": ">=",
               "value": 100,
               "next_node_id": end_node
              },
              {
               "kind": "weight_value_trigger",
               "source": "Weight Raw",
               "weight_reference_id": 1,
               "operator": ">=",
               "value": 36,
               "next_node_id": end_node
              },
              {
               "kind": "flow_value_trigger",
               "source": "Flow Raw",
               "operator": ">=",
               "value": 8,
               "next_node_id": 20
              },
              {
               "kind": "button_trigger",
               "source": "Encoder Button",
               "gesture": "Single Tap",
               "next_node_id": end_node
              }
             ]
            },
            {
             "id": 20,
             "controllers": [
              {
               "kind": "flow_controller",
               "algorithm": "Flow PID v1.0",
               "curve": {
                "id": 9,
                "interpolation_kind": "catmull_interpolation",
                "points": [
                 [
                  0,
                  8
                 ]
                ],
                "time_reference_id": 4
               }
              },
              {
               "kind": "position_reference",
               "id": 1
              }
             ],
             "triggers": [
              {
               "kind": "timer_trigger",
               "timer_reference_id": 4,
               "operator": ">=",
               "value": 100,
               "next_node_id": end_node
              },
              {
               "kind": "weight_value_trigger",
               "source": "Weight Raw",
               "weight_reference_id": 1,
               "operator": ">=",
               "value": 36,
               "next_node_id": end_node
              },
              {
               "kind": "pressure_curve_trigger",
               "source": "Pressure Raw",
               "operator": ">=",
               "curve_id": 7,
               "next_node_id": 13
              },
              {
               "kind": "button_trigger",
               "source": "Encoder Button",
               "gesture": "Single Tap",
               "next_node_id": end_node
              }
             ]
            }
        ]
     }
    return infusion_stage
    # return {}
    
if __name__ == '__main__':
  
    parameters = '{"preheat": true,"temperature": 200}'

    json_parameters = json.loads(parameters)

    infusion_stage = get_infusion_stage(json_parameters, 200, 1)
    print(json.dumps(infusion_stage, indent=4))