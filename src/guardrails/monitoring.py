import time

class MonitoringAlert:
    """
    Monitoring & Alerting system.
    Tracks metrics across the pipeline and fires alerts if thresholds are exceeded.
    """
    def __init__(self, plugins, block_threshold=0.3, rate_limit_threshold=5):
        self.plugins = {p.name: p for p in plugins if hasattr(p, 'name')}
        self.block_threshold = block_threshold  # 30% block rate threshold
        self.rate_limit_threshold = rate_limit_threshold # Max 5 block hits
        self.alerts = []

    def check_metrics(self):
        """Check all plugins for anomalies and fire alerts."""
        alerts_found = []
        
        # 1. Check Rate Limiter
        rl = self.plugins.get("rate_limiter")
        if rl and hasattr(rl, 'blocked_hits'):
            if rl.blocked_hits > self.rate_limit_threshold:
                alert = f"[ALERT] High frequency abuse detected! Rate limit hits: {rl.blocked_hits}"
                alerts_found.append(alert)

        # 2. Check Guardrails
        input_g = self.plugins.get("input_guardrail")
        if input_g and hasattr(input_g, 'total_count') and input_g.total_count > 0:
            block_rate = input_g.blocked_count / input_g.total_count
            if block_rate > self.block_threshold:
                alert = f"[ALERT] High violation rate! {block_rate*100:.1f}% of inputs are being blocked."
                alerts_found.append(alert)

        # 3. Output Guardrails (PII)
        output_g = self.plugins.get("output_guardrail")
        if output_g and hasattr(output_g, 'redacted_count') and output_g.redacted_count > 2:
            alert = f"[ALERT] Data leakage attempt! PII redacted {output_g.redacted_count} times."
            alerts_found.append(alert)

        self.alerts.extend(alerts_found)
        return alerts_found

    def print_status(self):
        print("\n" + "="*40)
        print("PIPELINE MONITORING STATUS")
        print("="*40)
        for name, p in self.plugins.items():
            if hasattr(p, 'total_count'):
                passed = p.total_count - (getattr(p, 'blocked_count', 0) or getattr(p, 'redacted_count', 0))
                print(f"{name:<15}: Total={p.total_count} | Blocked/Redacted={getattr(p, 'blocked_count', 0) or getattr(p, 'redacted_count', 0)}")
            elif name == "rate_limiter":
                print(f"{name:<15}: Total Hits={sum(len(w) for w in p.user_windows.values())} | Blocks={p.blocked_hits}")
        
        if self.alerts:
            print("\n🚨 ACTIVE ALERTS:")
            for a in self.alerts:
                print(f" - {a}")
        else:
            print("\n✅ System status: NORMAL")
        print("="*40 + "\n")
