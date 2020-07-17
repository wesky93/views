data "aws_acm_certificate" "custom_domain_cert" {
  domain = "views.whatilearened.today"
}
data "aws_route53_zone" "whatilearened" {
  name = "whatilearened.today."
}

resource "aws_api_gateway_domain_name" "custom_domain" {
  certificate_arn = data.aws_acm_certificate.custom_domain_cert.arn
  domain_name = data.null_data_source.chalice.inputs.stage == "dev" ? "views-dev.whatilearened.today" : "views.whatilearened.today"
}


resource "aws_api_gateway_base_path_mapping" "views" {
  api_id = aws_api_gateway_rest_api.rest_api.id
  stage_name = aws_api_gateway_deployment.rest_api.stage_name
  domain_name = aws_api_gateway_domain_name.custom_domain.domain_name
}

resource "aws_route53_record" "views" {
  name = aws_api_gateway_domain_name.custom_domain.domain_name
  type = "A"
  zone_id = data.aws_route53_zone.whatilearened.zone_id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.custom_domain.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.custom_domain.cloudfront_zone_id
  }
}