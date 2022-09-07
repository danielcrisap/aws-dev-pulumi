"""
Create VPC
"""
import pulumi
import pulumi_aws as aws
from src.defaults import aws_tags

MAIN_CIDR_PREFIX = "10.1."
MAIN_CIRD_BLOCKS = {
    "pub": ["0.0/20", "16.0/20", "32.0/20"],
    "pvt": ["48.0/20", "64.0/20", "80.0/20"],
    "db": ["192.0/20", "208.0/20", "224.0/20"],
}
K8S_CIDR_PREFIX = "100.64."
K8S_CIDR_BLOCKS = [
    "0.0/19",
    "32.0/19",
    "64.0/19",
]


def create_subnet(availability_zone: str,
                  workload_type: str,
                  vpc_id: str,
                  route_table_id: str,
                  cidr_block: str,
                  map_public_ip_on_launch: bool = False) -> str:
    """
    Create VPC Subnet and Assoc with Route Table
    """
    name = f"{workload_type}-{availability_zone}"
    aws_vpc_subnet = aws.ec2.Subnet(
        f'vpc-sb-{name}',
        tags=aws_tags(name=name, cost_center="10"),
        vpc_id=vpc_id,
        availability_zone=availability_zone,
        cidr_block=cidr_block,
        map_public_ip_on_launch=map_public_ip_on_launch,
    )
    aws.ec2.RouteTableAssociation(
        f'vpc-rt-assoc-{name}',
        subnet_id=aws_vpc_subnet.id,
        route_table_id=route_table_id,
    )
    return aws_vpc_subnet.id


vpc = aws.ec2.Vpc(
    "vpc",
    cidr_block=f"{MAIN_CIDR_PREFIX}0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags=aws_tags(name="vpc", cost_center="10"),
)

igw = aws.ec2.InternetGateway(
    "igw", vpc_id=vpc.id, tags=aws_tags(name="igw", cost_center="10")
)

secondary_cidr = aws.ec2.VpcIpv4CidrBlockAssociation(
    "secondaryCidr", vpc_id=vpc.id, cidr_block=f"{K8S_CIDR_PREFIX}0.0/16"
)

vpc_name = vpc.tags["Name"]

public_rt = aws.ec2.RouteTable(
    'rt-pub',
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
            cidr_block='0.0.0.0/0',
            gateway_id=igw.id
            )],
    tags=aws_tags(name="rt-pub", cost_center="10")
)


# Subnets, one for each AZ in as region
zone = aws.get_availability_zones()

subnet_ids = {
    "pub": [],
    "pvt": [],
    "db": [],
    "k8s": [],
}
for index, zone in enumerate(zone.names):
    #################################
    # Create Pub Subnets on each AZ #
    #################################
    cidr_block = MAIN_CIDR_PREFIX + MAIN_CIRD_BLOCKS["pub"][index]
    vpc_subnet = create_subnet(
        vpc_id=vpc.id,
        route_table_id=public_rt,
        availability_zone=zone,
        workload_type="pub",
        cidr_block=cidr_block,
        map_public_ip_on_launch=True
    )
    subnet_ids["pub"].append(vpc_subnet)

    #################################
    # Create K8s Subnets on each AZ #
    #################################
    cidr_block = K8S_CIDR_PREFIX + K8S_CIDR_BLOCKS[index]
    vpc_subnet = create_subnet(
        vpc_id=vpc.id,
        route_table_id=public_rt,
        availability_zone=zone,
        workload_type="k8s",
        cidr_block=cidr_block,
    )
    subnet_ids["k8s"].append(vpc_subnet)

pulumi.export("VPC_SUBNETS_IDS", subnet_ids)
