def remove_duplicates(messages):
    seen = set()
    unique_messages = []

    for message in messages:
        # Create tuple of values to check uniqueness
        message_key = (
            message.get('loan_id'),
            message.get('transaction_id'), 
            message.get('vendor'),
            message.get('priority'),
            message.get('unique_id')
        )
        
        # Only add message if we haven't seen this combination before
        if message_key not in seen:
            seen.add(message_key)
            unique_messages.append(message)
            
    return unique_messages
