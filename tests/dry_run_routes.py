import sys, os, json, traceback, inspect
sys.path.insert(0, os.path.abspath('python-backend'))
from fastapi.testclient import TestClient
from main import app, registry
from core.state import state_manager
from core.geoai.tool_registry import tool_registry

client = TestClient(app)

print('=== 1. AUDITING ROUTES AND FRONTEND CLIENT ENDPOINTS ===')
routes = []
for route in app.routes:
    methods = getattr(route, 'methods', None)
    path = getattr(route, 'path', None)
    routes.append({'path': path, 'methods': list(methods) if methods else []})

print(f'Total registered FastAPI routes: {len(routes)}')
for r in routes:
    methods_str = ",".join(r['methods'])
    path_str = r['path']
    print(f'  [{methods_str}] {path_str}')

fe_endpoints_to_test = [
 ('GET', '/'),
 ('GET', '/health'),
 ('GET', '/modules'),
 ('POST', '/api/execute', {'moduleId': 'classification', 'functionId': 'bulkunitweight', 'args': {'saturation': 0.8, 'voidratio': 0.6}}),
 ('GET', '/api/objects/SoilProfile'),
 ('GET', '/api/objects/SoilProfile/dummy_id'),
 ('POST', '/api/objects/create?type_name=SoilProfile', {'raw_data': [{'Depth from [m]': 0, 'Depth to [m]': 5, 'Unit weight [kN/m3]': 18}]}),
 ('GET', '/api/schema/overrides'),
 ('POST', '/api/schema/override', {'functionId': 'bulkunitweight', 'fieldName': 'saturation', 'metadata': {'help': 'test'}}),
 ('GET', '/api/geoai/tools'),
 ('GET', '/api/geoai/tools/format/openai'),
 ('GET', '/api/geoai/tools/format/gemini'),
 ('GET', '/api/geoai/tools/format/raw'),
 ('POST', '/api/geoai/invoke', {'tool_name': 'bulkunitweight', 'args': {'saturation': 0.8, 'voidratio': 0.6}}),
 ('POST', '/api/geoai/chat', {'prompt': 'Calculate bearing capacity for a 2m wide footing at 1m depth in sand with friction angle 32 degrees'}),
 ('POST', '/api/geoai/autofill', {'function_id': 'bulkunitweight', 'raw_text': 'saturation is 80% and void ratio is 0.6'}),
 ('GET', '/api/soilprofiles'),
 ('GET', '/api/calculationgrids'),
 ('POST', '/api/soilprofiles', {}),
 ('POST', '/api/calculationgrids', {})
]

route_audit_results = []
for item in fe_endpoints_to_test:
    method = item[0]
    path = item[1]
    body = item[2] if len(item) > 2 else None
    
    try:
        if method == 'GET':
            resp = client.get(path)
        elif method == 'POST':
            resp = client.post(path, json=body)
        elif method == 'DELETE':
            resp = client.delete(path)
        route_audit_results.append({
            'method': method,
            'path': path,
            'status_code': resp.status_code,
            'response_preview': str(resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text)[:200]
        })
    except Exception as e:
        route_audit_results.append({
            'method': method,
            'path': path,
            'status_code': 'EXCEPTION',
            'error': str(e)
        })

print('\nRoute Audit Summary:')
for res in route_audit_results:
    m = res['method']
    p = res['path']
    s = res['status_code']
    print(f' [{m}] {p} -> {s}')

with open('tests/route_audit_results.json', 'w') as f:
    json.dump(route_audit_results, f, indent=2)
