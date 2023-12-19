import pkgutil
import inspect
import importlib

def list_methods(package_name, output_file):

    try:
        package = importlib.import_module(package_name)
    except ImportError as e:
        print(f"Error importing package: {e}")
        return

    with open(output_file, 'w') as file:
        file.write(f"Package: {package_name}\n")
        for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
            try:
                module = importlib.import_module(modname)
                if len(modname.split('.')) == 2:
                    file.write(f"\tRoot Module: {modname.split('.')[-1]}\n")
                if len(modname.split('.')) > 2:
                    file.write(f"\t\tModule: {modname.split('.')[-1]}\n")
            except ImportError as e:
                print(f"Error importing module {modname}: {e}")
                continue

            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if the class is defined in this module
                if obj.__module__ == module.__name__:
                    file.write(f"\t\t\tClass: {name}\n")
                    for method_name, method_obj in inspect.getmembers(obj, inspect.isfunction):
                        # Check if the method is defined in this class
                        if method_obj.__module__ == module.__name__:
                            file.write(f"\t\t\t\tMethod: {method_name}\n")



# Usage
package_name = 'crystalaspects'
output_file = 'methods_list.txt'
list_methods(package_name, output_file)
