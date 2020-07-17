resource "aws_dynamodb_table" "views_count_table" {
  name           = "ViewsCountTable_${data.null_data_source.chalice.inputs.stage}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "page_id"

  attribute {
    name = "page_id"
    type = "S"
  }

  attribute {
    name = "service"
    type = "S"
  }

  attribute {
    name = "total_views"
    type = "N"
  }


  global_secondary_index {
    name               = "TotalViewRanking"
    hash_key           = "service"
    range_key          = "total_views"
    projection_type    = "ALL"
  }

  tags = {
    Project        = "views"
  }
}