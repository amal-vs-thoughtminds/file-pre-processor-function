def split_file_name(file_name: str) -> dict:
    try:
        name_without_ext = file_name.rsplit('.', 1)[0]
        
        parts = name_without_ext.split('_')
        
        if len(parts) != 5:
            raise ValueError(f"Invalid file name format: {file_name}")
        return {
            'unique_id': parts[0].lower(),
            'loan_id': parts[1].lower(),
            'transaction_id': parts[2].lower(), 
            'vendor': parts[3].lower(),
            'priority': parts[4].lower(),
            'file_name': file_name
        }
        
    except Exception as e:
        raise ValueError(f"Error parsing file name {file_name}: {str(e)}")