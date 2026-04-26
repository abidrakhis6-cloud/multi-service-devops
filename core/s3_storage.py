"""
S3 Storage utility for user data
Stores user registrations (name, email, message) as JSON in S3
"""
import json
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from datetime import datetime
import uuid


class S3UserStorage:
    """Handle user data storage in S3"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    def save_user_data(self, name, email, message):
        """
        Save user registration data to S3 as JSON
        
        Args:
            name: User name
            email: User email
            message: User message
            
        Returns:
            dict: {'success': True, 'file_key': 'path/to/file.json'} or {'success': False, 'error': 'message'}
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            file_key = f"users/{timestamp}_{unique_id}_{email.replace('@', '_at_')}.json"
            
            # Create user data object
            user_data = {
                'id': str(uuid.uuid4()),
                'name': name,
                'email': email,
                'message': message,
                'created_at': datetime.now().isoformat(),
                'source': 'multiserve_web',
                'ip_address': None
            }
            
            # Convert to JSON
            json_data = json.dumps(user_data, indent=2, ensure_ascii=False)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'email': email,
                    'name': name,
                    'created': timestamp
                }
            )
            
            return {
                'success': True,
                'file_key': file_key,
                'user_id': user_data['id']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
    
    def get_user_data(self, file_key):
        """Retrieve user data from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            data = json.loads(response['Body'].read().decode('utf-8'))
            return {'success': True, 'data': data}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def list_all_users(self, prefix='users/'):
        """List all user files in S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat()
                    })
            
            return {'success': True, 'files': files, 'count': len(files)}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def delete_user_data(self, file_key):
        """Delete user data from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return {'success': True}
        except ClientError as e:
            return {'success': False, 'error': str(e)}


# Singleton instance
s3_storage = S3UserStorage()
