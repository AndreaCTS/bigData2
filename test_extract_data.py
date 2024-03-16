import unittest
from unittest.mock import Mock, patch
from extract_data import handler, extract_data  


class TestLambdaHandlerProcessing(unittest.TestCase):
    @patch('extract_data.boto3.client')
    @patch('extract_data.boto3.resource')
    
    def test_lambda_handler_processing(
            self, mock_boto3_resource, mock_boto3_client):
        # Simulate the behavior of boto3
        mock_s3_resource = mock_boto3_resource.return_value
        # mock_s3_client = mock_boto3_client.return_value

        # Mock the S3 object and its get method
        mock_s3_object = Mock()
        mock_s3_resource.Object.return_value = mock_s3_object
        mock_s3_object.get.return_value = {
            'Body': Mock(read=Mock(return_value=b"HTML Content"))}

        # Execute the function under test
        result = handler(None, None)

        # Verify calls and behavior
        self.assertEqual(result['statusCode'], 200)
        # Add more assertions as necessary
    
    
    def test_extract_data(self):
        # HTML Content with known data
        html_content = """
        <div class="listing-card__information">
            <div class="price">$100,000</div>
            <div class="card-icon card-icon__area"><span>200 m²</span></div>
            <span data-test="bedrooms">3 Bedrooms</span>
            <span class="facility-item__text">Garden</span>
        </div>
        """
        expected_data = [['$100,000', '200 m²', '3 Bedrooms', 'Garden']]
        extracted_data = extract_data(html_content)
        self.assertEqual(extracted_data, expected_data)

        # Test with missing data
        html_content_missing = """
        <div class="listing-card__information">
            <div class="price">$100,000</div>
            <div class="card-icon card-icon__area"><span>200 m²</span></div>
            <span class="facility-item__text">Garden</span>
        </div>
        """
        expected_data_missing = [['$100,000', '200 m²', 'No disponible', 'Garden']]
        extracted_data_missing = extract_data(html_content_missing)
        self.assertEqual(extracted_data_missing, expected_data_missing)


if __name__ == '__main__':
    unittest.main()