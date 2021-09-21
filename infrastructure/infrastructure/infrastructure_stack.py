import aws_cdk.aws_applicationautoscaling as aws_applicationautoscaling
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ecs_patterns as ecs_patterns
import aws_cdk.aws_iam as iam
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
            cors=[
                s3.CorsRule(
                    allowed_methods=[
                        s3.HttpMethods.GET,
                    ],
                    allowed_origins=[
                        "http://localhost:3000",
                        "https://awesome-crawler.allocsoc.net",
                    ],
                    allowed_headers=["*"],
                )
            ],
        )

        zone = r53.HostedZone.from_lookup(self, "baseZone", domain_name="allocsoc.net")

        r53.CnameRecord(
            self,
            "test.baseZone",
            zone=zone,
            record_name="awesome-crawler",
            domain_name=bucket.bucket_website_domain_name,
        )

        s3ListBucketsPolicy = iam.PolicyStatement(
            actions=["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
            effect=iam.Effect.ALLOW,
            resources=[bucket.arn_for_objects("*")],
        )

        cluster = ecs.Cluster(self, "AwesomeCrawler")

        scheduled_fargate_task = ecs_patterns.ScheduledFargateTask(
            self,
            "ScheduledFargateTask",
            cluster=cluster,
            scheduled_fargate_task_image_options=ecs_patterns.ScheduledFargateTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(repository),
                memory_limit_mib=512,
            ),
            schedule=aws_applicationautoscaling.Schedule.cron(minute="0", hour="1"),
            platform_version=ecs.FargatePlatformVersion.LATEST,
        )

        scheduled_fargate_task.task_definition.add_to_task_role_policy(
            s3ListBucketsPolicy
        )
