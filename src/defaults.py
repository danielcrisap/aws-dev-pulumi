"""
Define default values from AWS Config
"""
import pulumi

AWS_TAGS = {
    "Pulumi": True,
    "Environment": pulumi.get_stack()
}


def aws_tags(name: str,
             cost_center: str) -> dict:
    """
    Define AWS Tags
    """
    name_n_cc = {"Name": f"{pulumi.get_stack()}-{name}",
                 "CC": cost_center}

    return {**AWS_TAGS,
            **name_n_cc}
