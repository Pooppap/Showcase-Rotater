import yaml


def parse_yaml(yaml_file, args):
    opts = vars(args)
    with open(yaml_file, "r") as _file:
        yaml_dict = yaml.safe_load(_file)
    
    opts.update(yaml_dict)
