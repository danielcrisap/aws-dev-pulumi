"""An AWS Python Pulumi program"""
import pulumi
from src.vpc import vpc
from src.eks import eks_cluster

pulumi.export('VPC_ID', vpc.id)
pulumi.export('EKS', eks_cluster.name)
