"""An AWS Python Pulumi program"""
import pulumi
from src.vpc import vpc
from src.eks import eks

pulumi.export('VPC_ID', vpc.vpc.id)
pulumi.export('EKS', eks.eks_cluster.arn)
