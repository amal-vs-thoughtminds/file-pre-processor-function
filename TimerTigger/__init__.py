import datetime
import logging
import azure.functions as func
import azure.durable_functions as df

async def main(timer: func.TimerRequest, starter: str) -> None:
    logging.info("Timer trigger function started.")
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new("Orchestrator", None, None)
    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    logging.info(f"Timer trigger function executed at: {datetime.datetime.now()}")