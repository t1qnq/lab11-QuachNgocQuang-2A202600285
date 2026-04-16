import json
import time
from datetime import datetime
from google.adk.plugins import base_plugin

class AuditLogPlugin(base_plugin.BasePlugin):
    """
    Audit Log Plugin.
    Records every interaction (input, output, latency, blocks) to a central log.
    Required for production monitoring and auditing.
    """
    def __init__(self, log_file="audit_log.json"):
        super().__init__(name="audit_log")
        self.log_file = log_file
        self.logs = []
        self._current_request = {}

    async def on_user_message_callback(self, *, invocation_context, user_message):
        # Record start of a new request
        self._current_request = {
            "timestamp": datetime.now().isoformat(),
            "user_id": invocation_context.user_id if invocation_context else "unknown",
            "input": self._extract_text(user_message),
            "start_time": time.time(),
            "blocked": False,
            "block_reason": None
        }
        return None

    async def after_model_callback(self, *, callback_context, llm_response):
        # Record end of request and calculate latency
        latency = time.time() - self._current_request.get("start_time", time.time())
        output_text = self._extract_text_response(llm_response)
        
        # Check if the response indicates a block
        if "[GUARDRAIL_BLOCK]" in output_text or "[RATE_LIMIT]" in output_text:
            self._current_request["blocked"] = True
            self._current_request["block_reason"] = "plugin_blocked"

        entry = {
            **self._current_request,
            "output": output_text,
            "latency_ms": round(latency * 1000, 2)
        }
        
        # Remove internal timing key before saving
        if "start_time" in entry:
            del entry["start_time"]
            
        self.logs.append(entry)
        self.export_json()
        return llm_response

    def _extract_text(self, content):
        if hasattr(content, 'parts'):
            return "".join([p.text for p in content.parts if hasattr(p, 'text')])
        return str(content)

    def _extract_text_response(self, response):
        if hasattr(response, 'content'):
            return self._extract_text(response.content)
        return str(response)

    def export_json(self, filepath=None):
        path = filepath or self.log_file
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
