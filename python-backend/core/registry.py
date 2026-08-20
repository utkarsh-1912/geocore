# Author: Utkarsh Gupta
# License: GPL v2

import inspect
import pkgutil
import importlib
import groundhog
from pydantic import create_model
from typing import Any, Dict, List, Optional

class Registry:
    def __init__(self):
        self.modules = {}
        self.function_map = {}
        self._scan_library()

    def _scan_library(self):
        """Scans the groundhog library for all submodules and functions."""
        import pkgutil
        import importlib
        import inspect
        import groundhog

        path = groundhog.__path__
        prefix = groundhog.__name__ + "."

        for _, name, ispkg in pkgutil.walk_packages(path, prefix):
            if ispkg:
                continue
            
            try:
                module = importlib.import_module(name)
                for func_name, obj in inspect.getmembers(module):
                    if (inspect.isfunction(obj) or inspect.isclass(obj)) and \
                       getattr(obj, '__module__', '') == module.__name__:
                        if not func_name.startswith("_"):
                            self.function_map[func_name] = obj
            except Exception as e:
                # Some modules might fail to import due to missing optional dependencies
                pass
        
        # Scan manual_functions.py
        try:
            from core import manual_functions
            importlib.reload(manual_functions) # Ensure we get the latest version
            for func_name, obj in inspect.getmembers(manual_functions):
                if inspect.isfunction(obj) and not func_name.startswith("_"):
                     # Add to map (will overwrite groundhog if same name, or add if unique)
                     # If you want manual to be fallback only, check using 'if func_name not in self.function_map:'
                     # But usually manual overrides are preferred if same name.
                     # User said "check the function in that if not found in library", so fallback logic:
                     if func_name not in self.function_map:
                         self.function_map[func_name] = obj
        except ImportError:
            pass # manual_functions.py might not exist or verify fail
        except Exception as e:
            print(f"Error loading manual_functions: {e}")

    def _sanitize(self, obj):
        import numpy as np
        import math
        import pandas as pd

        if obj is None:
            return None
        
        # Handle Pandas types
        if isinstance(obj, pd.DataFrame):
             return self._sanitize(obj.to_dict(orient='records'))
        if isinstance(obj, pd.Series):
             return self._sanitize(obj.to_dict())
             
        # Handle Numpy Arrays and Scalars
        if isinstance(obj, (np.ndarray, np.generic)):
            if isinstance(obj, np.ndarray):
                return self._sanitize(obj.tolist())
            else:
                 # Scalar numpy type
                 val = obj.item()
                 return self._sanitize(val)
        
        # Handle Dicts and Lists (Recursion)
        if isinstance(obj, dict):
            return {k: self._sanitize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._sanitize(v) for v in obj]

        # Handle Floats (Final check after containers)
        if isinstance(obj, float): 
            # Note: bool is distinct from float in Python, but isinstance(True, int) is True.
            # isinstance(1.0, float) is True.
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
            
        return obj

    def _parse_list(self, val):
        import json
        if isinstance(val, str):
            if not val.strip():
                return []
            try:
                # Try JSON (for arrays from frontend if they were stringified)
                return json.loads(val)
            except:
                # Try comma-separated
                try:
                    return [float(x.strip()) for x in val.split(',') if x.strip()]
                except:
                    # Fallback to list of strings
                    return [x.strip() for x in val.split(',') if x.strip()]
        return val

    def _map_args(self, func, args):
        import inspect
        sig = inspect.signature(func)
        func_args = {}
        for param_name, param in sig.parameters.items():
            if param_name in args:
                val = args[param_name]
                if val is not None and val != "":
                    try:
                        # But first, check if it should be a list
                        if isinstance(val, str) and (',' in val or val.startswith('[') or param_name in ['times', 'settlements', 'll', 'pi', 'grainsize', 'pctpassing', 'depths', 'data', 'requested_depths']):
                            func_args[param_name] = self._parse_list(val)
                        else:
                            func_args[param_name] = float(val) if isinstance(val, (int, float, str)) and param_name != 'Ngamma_theory' else val
                    except ValueError:
                        func_args[param_name] = val
        return func_args

    def find_function(self, function_id):
        return self.function_map.get(function_id)

    def execute_function(self, module_id: str, function_id: str, args: dict):
        from .state import state_manager
        import pandas as pd
        import inspect
        import importlib
        import pkgutil
        import warnings
        import numpy as np
        import math
        import json

        # 1. Handle Special Cases (Stateful objects like SoilProfile)
        if function_id == 'SoilProfile':
            from groundhog.general.soilprofile import SoilProfile
            
            file_path = args.get('data')
            raw_data = args.get('raw_data')  # List of dicts

            if raw_data:
                df = pd.DataFrame(raw_data)
            elif file_path:
                # Load data based on extension
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file_path)
                else:
                    raise ValueError("Unsupported file format")
            else:
                 raise ValueError("No file path or raw data provided for SoilProfile")

            # Rename columns
            depth_from = args.get('depth_from_col')
            depth_to = args.get('depth_to_col')
            
            if depth_from and depth_from in df.columns:
                df = df.rename(columns={depth_from: 'Depth from [m]'})
            if depth_to and depth_to in df.columns:
                df = df.rename(columns={depth_to: 'Depth to [m]'})
            
            # Ensure unique columns before processing
            df = df.loc[:, ~df.columns.duplicated()]

            # Robust numeric coercion for all columns
            # This handles cases where numbers are sent as strings from the frontend or parsed as strings from CSV
            for col in df.columns:
                try:
                    # Try to convert to numeric, coercing errors to NaN
                    numeric_col = pd.to_numeric(df[col], errors='coerce')
                    # If the conversion resulted in at least one number, use the numeric version
                    if isinstance(numeric_col, pd.Series) and numeric_col.notna().any():
                        df[col] = numeric_col
                except Exception:
                    pass

            # Normalize headers to ensure groundhog compatibility (requires [units])
            new_cols = {}
            import re
            for col in df.columns:
                 if not isinstance(col, str): continue
                 
                 # Skip depth columns which are already handled or standard
                 if col in ['Depth from [m]', 'Depth to [m]']:
                     continue
                 
                 if '[' not in col and ']' not in col:
                     # Try to detect unit suffix (e.g. _kPa, _m, _kN_m3)
                     match = re.search(r'_([a-zA-Z0-9_]+)$', col)
                     if match:
                         unit = match.group(1)
                         name = col[:match.start()]
                         new_col_name = f"{name} [{unit}]"
                     elif pd.api.types.is_numeric_dtype(df[col]):
                         new_col_name = f"{col} [-]"
                     else:
                         continue
                     
                     # Ensure we don't collide with existing columns
                     if new_col_name in df.columns or new_col_name in new_cols.values():
                         new_col_name = f"{new_col_name}_normalized"
                     new_cols[col] = new_col_name
            
            if new_cols:
                df = df.rename(columns=new_cols)

            nan_strategy = args.get('nan_strategy', 'fill')
            if nan_strategy == 'fill':
                # Only fill numeric columns to avoid mess in categorical ones
                numeric_df = df.select_dtypes(include=[np.number])
                df[numeric_df.columns] = numeric_df.fillna(0)
                
            profile = SoilProfile(df)
            obj_id = state_manager.store(profile, "SoilProfile")
            
            return {
                "type": "SoilProfile",
                "id": obj_id,
                "name": args.get('name', f"SoilProfile_{obj_id[:4]}"),
                "preview": self._sanitize(profile.head().to_dict(orient='records')),
                "layers": len(profile),
                "columns": list(profile.columns),
                "message": "Soil Profile created successfully."
            }

        if function_id == 'CalculationGrid':
            from groundhog.general.soilprofile import CalculationGrid
            profile_id = args.get('soilprofile')
            profile = state_manager.get(profile_id)
            if profile is None:
                return {"error": f"Soil Profile not found (ID: {profile_id}). The server may have reloaded. Please re-create the profile."}
            
            dz = float(args.get('dz', 0.5))
            include_transitions = args.get('include_layertransitions', True)
            if isinstance(include_transitions, str):
                include_transitions = include_transitions.lower() == 'true'
            
            grid = CalculationGrid(profile, dz, include_layertransitions=include_transitions)
            obj_id = state_manager.store(grid, "CalculationGrid")
            return {
                "type": "CalculationGrid",
                "id": obj_id,
                "nodes_count": len(grid.nodes) if hasattr(grid, 'nodes') else 0,
                "elements_count": len(grid.elements) if hasattr(grid, 'elements') else 0,
                "nodes": self._sanitize(grid.nodes.to_dict(orient='records')),
                "elements": self._sanitize(grid.elements.to_dict(orient='records')),
                "message": f"Calculation Grid created with dz={dz}"
            }

        # 2b. Lab Testing Wrappers
        if function_id in ['PlasticityChart', 'PSDChart', 'logtimemethod', 'roottimemethod']:
            from . import labtesting_wrappers
            # Map args before passing to wrappers
            # Since wrappers don't necessarily have the same signature as groundhog, 
            # we can pass calibrated args or just the raw args if the wrapper handles it.
            # However, mapping them here ensures lists are parsed.
            calibrated_args = self._map_args(getattr(labtesting_wrappers, f"{function_id.lower()}_wrapper"), args)
            
            if function_id == 'PlasticityChart':
                return labtesting_wrappers.plasticitychart_wrapper(calibrated_args)
            if function_id == 'PSDChart':
                return labtesting_wrappers.psdchart_wrapper(calibrated_args)
            if function_id == 'roottimemethod':
                return labtesting_wrappers.roottimemethod_wrapper(calibrated_args)
            if function_id == 'logtimemethod':
                return labtesting_wrappers.logtimemethod_wrapper(calibrated_args)

        # 2c. In-situ Processing Classes
        if function_id == 'PCPTProcessing':
            try:
                from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
                title = args.get('title', 'PCPT Analysis')
                water_unit_weight = float(args.get('waterunitweight', 10.25))
                
                pcpt = PCPTProcessing(title=title, waterunitweight=water_unit_weight)
                obj_id = state_manager.store(pcpt, "PCPTProcessing")
                
                return {
                    "type": "PCPTProcessing",
                    "id": obj_id,
                    "title": title,
                    "message": "PCPT Processing object created successfully."
                }
            except ImportError:
                return {"error": "PCPTProcessing class not found in groundhog."}
            except Exception as e:
                return {"error": f"Error creating PCPTProcessing: {str(e)}"}

        if function_id == 'SPTProcessing':
            try:
                from groundhog.siteinvestigation.insitutests.spt_processing import SPTProcessing
                title = args.get('title', 'SPT Analysis')
                water_unit_weight = float(args.get('waterunitweight', 10.0))
                
                spt = SPTProcessing(title=title, waterunitweight=water_unit_weight)
                obj_id = state_manager.store(spt, "SPTProcessing")
                
                return {
                    "type": "SPTProcessing",
                    "id": obj_id,
                    "title": title,
                    "message": "SPT Processing object created successfully."
                }
            except ImportError:
                 return {"error": "SPTProcessing class not found in groundhog."}
            except Exception as e:
                return {"error": f"Error creating SPTProcessing: {str(e)}"}

        # 2d. AGS Converter
        if function_id == 'AGSConverter':
            from groundhog.general.agsconversion import AGSConverter
            file_path = args.get('data')
            if not file_path:
                 raise ValueError("No file path provided for AGSConverter")
            
            converter = AGSConverter(
                file_path, 
                encoding=args.get('encoding', 'utf8'),
                agsformat=args.get('agsformat', '4')
            )
            # Scan group names
            converter.extract_groupnames()
            
            obj_id = state_manager.store(converter, "AGSConverter")
            return {
                "type": "AGSConverter",
                "id": obj_id,
                "name": args.get('name', f"AGS_{obj_id[:4]}"),
                "groupnames": sorted(list(converter.groupnames)),
                "message": "AGS file loaded successfully."
            }

        if function_id == 'AGSConverter_convert_ags_group':
            ags_id = args.get('agsconverter')
            converter = state_manager.get(ags_id)
            if not converter:
                raise ValueError(f"AGSConverter with ID {ags_id} not found")
            
            groupname = args.get('groupname')
            df = converter.convert_ags_group(
                groupname,
                verbose_keys=args.get('verbose_keys', False),
                use_shorthands=args.get('use_shorthands', False)
            )
            
            return {
                "type": "dataframe",
                "data": self._sanitize(df.to_dict(orient='records')),
                "columns": list(df.columns),
                "message": f"Extracted group {groupname}"
            }


        # 3. Hardening Soil Model
        if function_id == 'hardening_soil_drained_triaxial':
            try:
                from groundhog.constitutivemodels.cohesionless import HardeningSoil
            except ImportError:
                 return {"error": "groundhog.constitutivemodels module not found. Please ensure it is installed."}

            try:
                # Extract arguments
                # Material
                phi = float(args.get('friction_angle'))
                c = float(args.get('cohesion'))
                rf = float(args.get('Rf', 0.9))
                
                # Stiffness
                e50 = float(args.get('E50_ref'))
                eur = float(args.get('Eur_ref'))
                eoed = float(args.get('Eoed_ref'))
                p_ref = float(args.get('p_ref', 100))
                
                # Test
                s3 = float(args.get('sigma3'))
                s1_0 = float(args.get('sigma1_0'))
                m = float(args.get('m'))
                n = int(args.get('N', 100))

                # Initialize Model
                model = HardeningSoil(friction_angle=phi, cohesion=c, Rf=rf)
                model.set_reference_moduli(E50_ref=e50, Eur_ref=eur, Eoed_ref=eoed, p_ref=p_ref)
                
                # Run Calculation
                with warnings.catch_warnings(record=True) as caught_warnings:
                    warnings.simplefilter("always")
                    res = model.calculate_drainedtriaxial(sigma3=s3, sigma1_0=s1_0, m=m, N=n)
                
                warning_messages = [str(w.message) for w in caught_warnings]
                
                # Sanitize Result
                sanitized_res = self._sanitize(res)
                
                # Construct Plotly Data
                charts = []
                
                # Check for array keys in sanitized result
                if isinstance(sanitized_res, dict):
                    if 'epsilon_1' in sanitized_res and 'q' in sanitized_res:
                         charts.append({
                            "x": sanitized_res['epsilon_1'],
                            "y": sanitized_res['q'],
                            "type": "scatter",
                            "mode": "lines",
                            "name": "Deviator Stress (q) vs Axial Strain"
                        })
                    
                    if 'epsilon_1' in sanitized_res and 'epsilon_v' in sanitized_res:
                         charts.append({
                            "x": sanitized_res['epsilon_1'],
                            "y": sanitized_res['epsilon_v'],
                            "type": "scatter",
                            "mode": "lines",
                            "name": "Volumetric Strain vs Axial Strain",
                            "xaxis": "x",
                            "yaxis": "y2"
                        })

                if len(charts) > 0:
                    return {
                        "type": "plotly",
                        "data": charts,
                        "layout": {
                            "title": "Hardening Soil - Drained Triaxial Test",
                            "xaxis": { "title": "Axial Strain (epsilon_1)" },
                            "yaxis": { "title": "Deviator Stress (q) [kPa]" },
                            "yaxis2": {
                                "title": "Volumetric Strain",
                                "overlaying": "y",
                                "side": "right"
                            },
                            "legend": { "x": 1.1, "y": 1 }
                        },
                        "raw_data": sanitized_res,
                        "warnings": warning_messages
                    }
                
                # Fallback
                if isinstance(sanitized_res, dict):
                    sanitized_res['warnings'] = warning_messages
                    return sanitized_res
                return {"result": sanitized_res, "warnings": warning_messages}

            except Exception as e:
                return {"error": f"Hardening Soil Execution Error: {str(e)}"}

        # 4. Eurocode 7 Functions
        if function_id == 'parameter_selection_constant_value':
            from groundhog.standards.eurocode7 import parameter_selection
            
            try:
                # Map args
                raw_data = args.get('data', [])
                if isinstance(raw_data, str):
                    try:
                        data = json.loads(raw_data)
                    except:
                        data = [float(x.strip()) for x in raw_data.split(',')]
                else:
                    data = raw_data

                mode = args.get('mode', 'Low')
                covarg = args.get('cov')
                # Fixed: handle empty string or None safely
                if covarg == '' or covarg is None:
                    cov = float('nan')
                else:
                    cov = float(covarg)
                    
                # Validate Data Length
                if len(data) < 2 and (cov is None or math.isnan(cov)):
                     return {"error": "Error: At least 2 data points are required to calculate statistics when CoV is unknown."}

                confidence = float(args.get('confidence', 0.95))
                
                with warnings.catch_warnings(record=True) as caught_warnings:
                    warnings.simplefilter("always")
                    res = parameter_selection.constant_value(
                        data=data, mode=mode, cov=cov, confidence=confidence
                    )
                
                warning_messages = [str(w.message) for w in caught_warnings]
                sanitized_res = self._sanitize(res)
                
                if isinstance(sanitized_res, dict):
                    sanitized_res['warnings'] = warning_messages
                    return sanitized_res
                return {"result": sanitized_res, "warnings": warning_messages}

            except Exception as e:
                return {"error": f"Eurocode 7 Error: {str(e)}"}

        if function_id == 'parameter_selection_linear_trend':
            from groundhog.standards.eurocode7 import parameter_selection
            
            try:
                # Helper to parse lists
                def parse_list(val):
                    if isinstance(val, str):
                        try:
                            return json.loads(val)
                        except:
                            return [float(x.strip()) for x in val.split(',')]
                    return val

                data = parse_list(args.get('data'))
                depths = parse_list(args.get('depths'))
                req_depths = parse_list(args.get('requested_depths'))
                
                # Validation
                if len(data) < 2:
                     return {"error": "Error: At least 2 data points are required for linear trend analysis (n > 2 recommended)."}
                if len(data) != len(depths):
                     return {"error": f"Error: Mismatch between Data ({len(data)}) and Depths ({len(depths)})."}

                mode = args.get('mode', 'Low')
                confidence = float(args.get('confidence', 0.95))

                with warnings.catch_warnings(record=True) as caught_warnings:
                    warnings.simplefilter("always")
                    res = parameter_selection.linear_trend(
                        data=data, depths=depths, requested_depths=req_depths,
                        mode=mode, confidence=confidence
                    )
                
                warning_messages = [str(w.message) for w in caught_warnings]
                sanitized_res = self._sanitize(res)
                
                if isinstance(sanitized_res, dict):
                    sanitized_res['warnings'] = warning_messages
                    return sanitized_res
                return {"result": sanitized_res, "warnings": warning_messages}

            except Exception as e:
                return {"error": f"Eurocode 7 Linear Trend Error: {str(e)}"}

        if function_id == 'eurocode7_factors':
            from groundhog.standards.eurocode7.factors import Eurocode7_factoring_STR_GEO
            
            try:
                ec7 = Eurocode7_factoring_STR_GEO()
                
                da = args.get('design_approach', 'DA1-1')
                ft = args.get('foundation_type', 'Spread foundation')
                
                ec7.select_design_approach(design_approach=da, foundation_type=ft)
                
                return self._sanitize({
                    "actions": ec7.selected_factors_actions,
                    "soil": ec7.selected_factors_soil,
                    "resistance": ec7.selected_factors_resistance,
                    "message": f"Selected factors for {da} - {ft}"
                })
            except Exception as e:
                return {"error": f"Eurocode 7 Factors Error: {str(e)}"}

        if function_id in ['contactwidth', 'embedment_drained', 'embedment_undrained_method1', 'embedment_undrained_method2', 'lay_touchdown_factor', 'penetratedarea']:
            try:
                import groundhog.pipelinescables.stability.penetration as pen
                
                func = getattr(pen, function_id)
                
                # Map Arguments
                sig = inspect.signature(func)
                func_args = {}
                
                for param_name, param in sig.parameters.items():
                    if param_name in args:
                        val = args[param_name]
                        # Type coercion
                        if val is not None and val != "":
                            try:
                                # Attempt float conversion for numeric fields, except strings
                                func_args[param_name] = float(val) if isinstance(val, (int, float, str)) and not isinstance(val, str) or (isinstance(val, str) and val.replace('.','',1).isdigit()) else val
                                # Specific handling for string enums like Ngamma_theory
                                if param_name == 'Ngamma_theory':
                                     func_args[param_name] = str(val)
                            except ValueError:
                                func_args[param_name] = val
                
                with warnings.catch_warnings(record=True) as caught_warnings:
                    warnings.simplefilter("always")
                    res = func(**func_args)
                
                warning_messages = [str(w.message) for w in caught_warnings]
                sanitized_res = self._sanitize(res)
                
                if isinstance(sanitized_res, dict):
                    sanitized_res['warnings'] = warning_messages
                    return sanitized_res
                return {"result": sanitized_res, "warnings": warning_messages}

            except Exception as e:
                return {"error": f"Pipeline Function Error ({function_id}): {str(e)}"}

        if function_id == 'consolidation_calculation':
            try:
                from groundhog.consolidation.dissipation.onedimensionalconsolidation import ConsolidationCalculation
                
                # 1. Initialize
                height = float(args.get('height'))
                total_time = float(args.get('total_time'))
                no_nodes = int(args.get('no_nodes', 50))
                
                model = ConsolidationCalculation(height, total_time, no_nodes)
                
                # 2. Set Cv
                cv = float(args.get('cv'))
                model.set_cv(cv)
                
                # 3. Set Initial Conditions
                # Handle scalar or array u0
                u0_arg = args.get('u0')
                depths = np.linspace(0, height, no_nodes)
                
                if isinstance(u0_arg, (int, float)):
                    u0 = np.ones(no_nodes) * float(u0_arg)
                    model.set_initial(u0, depths)
                else:
                    # Try to parse array
                    try:
                        u0_arr = np.array(json.loads(u0_arg))
                        if len(u0_arr) != no_nodes:
                             # Interpolate if length mismatch
                             u0 = np.interp(depths, np.linspace(0, height, len(u0_arr)), u0_arr)
                        else:
                             u0 = u0_arr
                        model.set_initial(u0, depths)
                    except:
                        # Fallback to uniform 0 if parsing fails
                        u0 = np.zeros(no_nodes) 
                        model.set_initial(u0, depths)

                # 4. Set Boundaries
                model.set_top_boundary(freedrainage=args.get('freedrainage_top', True))
                model.set_bottom_boundary(freedrainage=args.get('freedrainage_bottom', True))
                
                # 5. Set Output Times (generate 50 steps for smooth plotting)
                output_times = np.linspace(0, total_time, 50)
                model.set_output_times(output_times)
                
                # 6. Calculate
                model.calculate()
                
                # 7. Extract Results
                # User requested specific structure: times, depths, u
                # We will output values corresponding to the *requested output times*.
                
                # Get indices for output times
                ids = model.output_indices if hasattr(model, 'output_indices') else list(range(len(model.u_steps)))
                
                # Extract subset of times and u corresponding to requested output times
                # model.times contains ALL steps, model.output_times contains requested ones (if set_output_times called)
                
                final_times = self._sanitize(model.output_times)
                final_depths = self._sanitize(model.z)
                
                # Construct u matrix (Rows=Time, Cols=Depth)
                u_matrix = []
                for idx in ids:
                    if idx < len(model.u_steps):
                        u_matrix.append(self._sanitize(model.u_steps[idx]))
                
                results = {
                    "times": final_times,
                    "depths": final_depths,
                    "u": u_matrix 
                }

                # Generate Plotly Chart (Isochrones)
                charts = []
                # Plot subset of isochrones to avoid clutter (e.g., max 10 lines)
                num_steps = len(results["times"])
                step = max(1, num_steps // 10)
                
                for i in range(0, num_steps, step):
                    t = results["times"][i]
                    u_vals = results["u"][i]
                    charts.append({
                        "x": u_vals,
                        "y": results["depths"],
                        "type": "scatter",
                        "mode": "lines",
                        "name": f"t = {t:.2e} s"
                    })
                
                # Always include the last step if not already included
                if num_steps > 0 and (num_steps - 1) % step != 0:
                     charts.append({
                        "x": results["u"][-1],
                        "y": results["depths"],
                        "type": "scatter",
                        "mode": "lines",
                        "name": f"t = {results['times'][-1]:.2e} s"
                    })

                return {
                    "type": "plotly",
                    "data": charts,
                    "layout": {
                        "title": "Isochrones (Excess Pore Pressure vs Depth)",
                        "xaxis": { "title": "Excess Pore Pressure [kPa]" },
                        "yaxis": { "title": "Depth [m]", "autorange": "reversed" }
                    },
                    "raw_data": results
                }

            except Exception as e:
                return {"error": f"Consolidation Calculation Error: {str(e)}"}


        if function_id in ['consolidation_degree', 'pore_pressure_fourier']:
            try:
                import groundhog.consolidation.dissipation.onedimensionalconsolidation as odc
                func = getattr(odc, function_id)
                
                # Standard execution
                sig = inspect.signature(func)
                func_args = {}
                for param_name, param in sig.parameters.items():
                    if param_name in args:
                        val = args[param_name]
                        if val is not None and val != "":
                            try:
                                func_args[param_name] = float(val) if isinstance(val, (int, float, str)) and param_name != 'distribution' else val
                            except ValueError:
                                func_args[param_name] = val
                
                with warnings.catch_warnings(record=True) as caught_warnings:
                    warnings.simplefilter("always")
                    res = func(**func_args)
                
                return self._sanitize({
                    "result": res,
                    "warnings": [str(w.message) for w in caught_warnings]
                })
            except Exception as e:
                return {"error": f"Consolidation Function Error ({function_id}): {str(e)}"}

        if function_id == 'LogPlot':
            import core.plotting_wrappers as plotting_wrappers
            import importlib
            importlib.reload(plotting_wrappers)
            return plotting_wrappers.log_plot_wrapper(args)

        if function_id == 'plot_with_log':
            # Use dedicated wrapper for plotting
            import core.plotting_wrappers as plotting_wrappers
            import importlib
            importlib.reload(plotting_wrappers)
            return plotting_wrappers.plot_with_log_wrapper(args)

        if function_id == 'LogPlotMatplotlib':
            try:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                from groundhog.general.plotting import LogPlotMatplotlib
                import io
                import base64
                
                profile_id = args.get('soilprofile')
                profile = state_manager.get(profile_id)
                if profile is None:
                    return {"error": f"SoilProfile {profile_id} not found"}

                params_str = args.get('parameters', "")
                param_list = [p.strip().strip("'").strip('"') for p in params_str.split(',') if p.strip()]
                
                if not param_list:
                     return {"error": "No parameters provided"}

                # Initialize Plotter (1 panel)
                # Detect likely soil type column
                soil_type_col = args.get('soiltypecolumn', 'Soil type')
                if soil_type_col not in profile.columns:
                    for c in ['Type', 'Soil', 'Material', 'SoilType', 'Lithology']:
                        if c in profile.columns:
                            soil_type_col = c
                            break
                
                plotter = LogPlotMatplotlib(profile, no_panels=1, soiltypecolumn=soil_type_col)
                
                for p in param_list:
                    # Attempt to plot. 
                    try:
                        plotter.add_soilparameter_trace(p, panel_no=1)
                    except Exception as e:
                         # Fallback: Try to find a column that looks like p
                         found = False
                         for col in profile.columns:
                             if not isinstance(col, str): continue
                             
                             if p.lower() in col.lower() or p.replace('_', ' ').lower() in col.lower():
                                 try:
                                     plotter.add_soilparameter_trace(col, panel_no=1)
                                     found = True
                                     break
                                 except: continue
                         if not found:
                             print(f"Skipping parameter '{p}': {str(e)}")
                             pass

                # Save to buffer
                buf = io.BytesIO()
                plotter.fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close(plotter.fig) 
                
                buf.seek(0)
                image_base64 = base64.b64encode(buf.read()).decode('utf-8')
                
                return {
                    "type": "image",
                    "data": image_base64,
                    "format": "png",
                    "soiltypecolumn": soil_type_col # Return so UI knows what was used
                }

            except Exception as e:
                import traceback
                print(f"DEBUG: LogPlotMatplotlib failed: {str(e)}")
                return {"error": f"LogPlotMatplotlib Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"}

        if function_id == 'settlement_calculation':
            try:
                from groundhog.shallowfoundations.settlement import SettlementCalculation
                
                # 1. Get Soil Profile
                profile_id = args.get('soilprofile')
                profile = state_manager.get(profile_id)
                if not profile:
                    return {"error": f"SoilProfile with ID {profile_id} not found."}

                # 2. Initialize Calculation
                # SettlementCalculation expects a SoilProfile object (pandas df wrapper)
                # Our 'profile' is a SoilProfile instance (from groundhog.general.soilprofile)
                calc = SettlementCalculation(profile)

                # 3. Set Foundation
                width = float(args.get('foundation_width', 1.0))
                length = float(args.get('foundation_length', 1.0))
                shape = args.get('foundation_shape', 'strip')
                calc.set_foundation(width=width, shape=shape, length=length)
                
                # Create Grid (Required)
                calc.create_grid()

                # 4. Set Loading and Water Level
                # Assuming default water level at 0 if not specified (can add to schema later)
                water_level = float(args.get('water_level', 0.0))
                calc.calculate_initial_state(waterlevel=water_level)
                
                applied_stress = float(args.get('applied_stress', 0.0))
                calc.calculate_foundation_stress(applied_stress=applied_stress)

                # 5. Calculate Settlement
                # calculate() might return something or just set state
                # It usually calculates settlement for the defined grid
                calc.calculate()

                # 6. Generate Plot
                # We want to return the settlement vs depth plot
                # plot_result() typically shows a plot. We need to capture the data.
                # groundhog plotting usually returns a plotly figure or matplotlib fig
                
                # Let's try to get the figure from plot_result
                fig = calc.plot_result(showfig=False)
                
                # If fig is a plotly Figure, we can serialize it
                import plotly
                
                # Extract data/layout
                plot_json = json.loads(plotly.io.to_json(fig))
                
                return {
                    "type": "plotly",
                    "data": plot_json['data'],
                    "layout": plot_json['layout'],
                    "message": "Settlement calculation completed successfully."
                }

            except Exception as e:
                return {"error": f"Settlement Calculation Error: {str(e)}"}

        if function_id == 'shallow_foundation_capacity_undrained':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.shallow_foundation_capacity_undrained_wrapper(args)

        if function_id == 'shallow_foundation_capacity_drained':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.shallow_foundation_capacity_drained_wrapper(args)

        if function_id == 'effectivearea_circle_api':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.effectivearea_circle_wrapper(args)

        if function_id == 'effectivearea_rectangle_api':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.effectivearea_rectangle_wrapper(args)
        
        if function_id == 'map_depth_properties':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.map_depth_properties_wrapper(args)

        if function_id == 'offsets_api':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.offsets_wrapper(args)

        if function_id == 'merge_two_dicts':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.merge_two_dicts_wrapper(args)

        if function_id == 'reverse_dict':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.reverse_dict_wrapper(args)
        

        if function_id == 'AxCapCalculation':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.axcap_calculation_wrapper(args)

        if function_id == 'DeBeerCalculation':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.debeer_calculation_wrapper(args)

        if function_id == 'KoppejanCalculation':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.koppejan_calculation_wrapper(args)

        if function_id == 'LCPC_Calculation':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.lcpc_calculation_wrapper(args)

        if function_id == 'PileSettlementCurves':
            import importlib
            from . import wrappers
            importlib.reload(wrappers)
            return wrappers.pile_settlement_curves_wrapper(args)

        # Lateral Response
        if function_id == 'pilegroupeffect_reesevanimpe':
            import core.wrappers as wrappers
            import importlib
            importlib.reload(wrappers)
            return self._sanitize(wrappers.pilegroupeffect_reesevanimpe_wrapper(args))

        if function_id == 'reinforced_circularsection_inertia':
            import core.wrappers as wrappers
            import importlib
            importlib.reload(wrappers)
            return self._sanitize(wrappers.reinforced_circularsection_inertia_wrapper(args))

        # Cavity Expansion
        if function_id == 'expansion_cylinder_tresca':
            import core.wrappers as wrappers
            import importlib
            importlib.reload(wrappers)
            return self._sanitize(wrappers.expansion_cylinder_tresca_wrapper(args))

        if function_id == 'expansion_tresca_thicksphere':
            import core.wrappers as wrappers
            import importlib
            importlib.reload(wrappers)
            return self._sanitize(wrappers.expansion_tresca_thicksphere_wrapper(args))

        if function_id == 'stress_cylinder_elastic_isotropic':
            import core.wrappers as wrappers
            import importlib
            importlib.reload(wrappers)
            return self._sanitize(wrappers.stress_cylinder_elastic_isotropic_wrapper(args))

        # Negative Skin Friction
        if function_id == 'negativeskinfriction_pilegroup_zeevaertdebeer':
            import core.wrappers as wrappers
            import importlib
            importlib.reload(wrappers)
            return self._sanitize(wrappers.negativeskinfriction_pilegroup_zeevaertdebeer_wrapper(args))

        # Pile Testing
        if function_id == 'piletest_chinkondler':
            import core.wrappers as wrappers
            import importlib
            importlib.reload(wrappers)
            return self._sanitize(wrappers.piletest_chinkondler_wrapper(args))

        # Generic Handler for Stateless Functions
        try:
            # First, try to find the function if not handled specifically above
            # We already checked special cases, so now we use the generic lookup
                 
            func = self.find_function(function_id)
            if not func:
                return {"status": "Error", "error": f"Function {function_id} not found in groundhog library. Checked path: {groundhog.__path__}"}
    
            # Map Arguments
            func_args = self._map_args(func, args)
            
            print(f"DEBUG: Executing {function_id} with args: {func_args}")
            
            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always") 
                result = func(**func_args)
            
            sanitized_result = self._sanitize(result)
            warning_messages = [str(w.message) for w in caught_warnings]
            
            if isinstance(sanitized_result, dict):
                if warning_messages:
                    sanitized_result['warnings'] = warning_messages
                return sanitized_result
            else:
                return {
                    "result": sanitized_result,
                    "warnings": warning_messages
                }
        

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"Execution error in {function_id}: {str(e)}"}

    def get_modules(self) -> List[str]:
        return list(self.modules.keys())

    def get_functions(self, module_name: str) -> Dict[str, Any]:
        return self.modules.get(module_name, {}).get("functions", {})

registry = Registry()
