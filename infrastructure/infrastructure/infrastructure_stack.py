import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_iam as iam
from aws_cdk import core as cdk


class InfrastructureStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repository = ecr.Repository(self, "awesome-crawler")
        user = iam.User(self, "AWESOME_CRAWLER_GITHUB_ACTIONS_PUSH_ECR")
        ecr.AuthorizationToken.grant_read(user)

        repository.add_lifecycle_rule(max_image_count=5)

        repository.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:GetRepositoryPolicy",
                    "ecr:DescribeRepositories",
                    "ecr:ListImages",
                    "ecr:DescribeImages",
                    "ecr:BatchGetImage",
                    "ecr:GetLifecyclePolicy",
                    "ecr:GetLifecyclePolicyPreview",
                    "ecr:ListTagsForResource",
                    "ecr:DescribeImageScanFindings",
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload",
                    "ecr:PutImage",
                ],
                principals=[user],
            )
        )
