import pulumi
from pulumi_aws import eks
from pulumi_aws import ec2
import src.eks_iam as iam
from src.vpc import vpc, subnet_ids

# Security Group
eks_security_group = ec2.SecurityGroup(
    'eks-cluster-sg',
    vpc_id=vpc.id,
    description='Allow all HTTP(s) traffic to EKS Cluster',
    tags={
        'Name': 'pulumi-cluster-sg',
    },
    ingress=[
        ec2.SecurityGroupIngressArgs(
            cidr_blocks=['0.0.0.0/0'],
            from_port=443,
            to_port=443,
            protocol='tcp',
            description='Allow pods to communicate with the cluster API Server.'
        ),
        ec2.SecurityGroupIngressArgs(
            cidr_blocks=['0.0.0.0/0'],
            from_port=80,
            to_port=80,
            protocol='tcp',
            description='Allow internet access to pods'
        ),
    ],
)

# EKS Cluster
eks_cluster = eks.Cluster(
    'eks-cluster',
    role_arn=iam.eks_role.arn,
    tags={
        'Name': 'pulumi-eks-cluster',
    },
    vpc_config=eks.ClusterVpcConfigArgs(
        public_access_cidrs=['0.0.0.0/0'],
        security_group_ids=[eks_security_group.id],
        subnet_ids=subnet_ids["k8s"],
    ),
)

pulumi.export('cluster-name', eks_cluster.name)
