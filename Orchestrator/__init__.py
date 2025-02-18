import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    # 1. Get the configuration from DB (contains vendor queue names)
    config = yield context.call_activity("GetConfigs", None)
    
    # Assuming config is a list of dictionaries
    # print("Config:", config)
    vendor_queues = []
    if isinstance(config, list):
        vendor_queues = config
    else:
        print("Unexpected config format:", config)

    # print("Vendor Queues:", vendor_queues)
    
    total_required = 32
    messages = []
    
    # # 2. Pull messages from each vendor queue until we have 32 in total.
    for queue in vendor_queues:
        print("Queue:", queue)
        if not queue:
            continue
        if len(messages) >= total_required:
            break
        remaining = total_required - len(messages)
        queue_msgs = yield context.call_activity("GetQueueMessages", {"queue_name": queue, "max_messages": remaining})
        messages.extend(queue_msgs)
        
    # 3. Process each file message
    processed_results = []
    if len(messages) > 0:
        for msg in messages:
            result = yield context.call_activity("FilePreProcessor", msg)
            if result != 'Error':
                processed_results.append(result)
        
    # 4. Push successful results to next queue (e.g., loan_id_tnxId_vendor_priority) 
    if len(processed_results) > 0:
        stage = "classification"
        yield context.call_activity("PushToNextQueue", {"stage": stage, "processed_results": processed_results})
    
    return "Orchestration completed."
    
main = df.Orchestrator.create(orchestrator_function)
