
import sys
import os

# Add site-packages to path if needed (though groundhog should be installed in venv)
# We assume running with the venv python

try:
    from groundhog.deepfoundations.boreholestability.cavityexpansion import expansion_tresca_thicksphere
except ImportError:
    print("Could not import groundhog. Make sure you are running with the project's venv.")
    sys.exit(1)

def check_keys():
    print("Running expansion_tresca_thicksphere...")
    try:
        res = expansion_tresca_thicksphere(
            undrained_shear_strength=12,
            internal_radius=10,
            external_radius=15,
            internal_pressure=20,
            external_pressure=39,
            youngs_modulus=120,
            poissons_ratio=0.5,
            seed=100
        )
        print("\nKeys returned:")
        for k in res.keys():
            print(f"- '{k}'")
            
        print(f"\nValues types:")
        for k, v in res.items():
            print(f"- {k}: {type(v)}")

    except Exception as e:
        print(f"Error running function: {e}")

if __name__ == "__main__":
    check_keys()
