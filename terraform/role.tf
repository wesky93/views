resource "aws_iam_policy" "lambda_policy" {
  name        = "views_lambda_policy_${data.null_data_source.chalice.inputs.stage}"
  description = "views lambda resource access policy"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "dynamodb:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "test-attach" {
  role       = aws_iam_role.default-role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}