import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as events_targets
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as aws_lamba
import aws_cdk.aws_route53 as r53
import aws_cdk.aws_s3 as s3
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

        bucket = s3.Bucket(
            self,
            "awesome-crawler-bucket",
            bucket_name="awesome-crawler.allocsoc.net",
            public_read_access=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            website_index_document="index.html",
        )

        zone = r53.HostedZone.from_lookup(self, "baseZone", domain_name="allocsoc.net")

        r53.CnameRecord(
            self,
            "test.baseZone",
            zone=zone,
            record_name="awesome-crawler",
            domain_name=bucket.bucket_website_domain_name,
        )

        func = aws_lamba.DockerImageFunction(
            self,
            "AWESOME_CRAWELER_DAILY",
            code=aws_lamba.DockerImageCode.from_ecr(repository),
        )

        eventRule = events.Rule(
            self,
            "awesome_craweler_daily",
            schedule=events.Schedule.cron(minute="0", hour="1"),
        )

        eventRule.add_target(events_targets.LambdaFunction(func))

        s3ListBucketsPolicy = iam.PolicyStatement(
            actions=["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
            effect=iam.Effect.ALLOW,
            resources=[bucket.arn_for_objects("*")],
        )

        role = func.role
        if role:
            role.attach_inline_policy(
                iam.Policy(self, "rw s3 policy", statements=[s3ListBucketsPolicy])
            )
