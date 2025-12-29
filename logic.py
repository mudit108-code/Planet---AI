def consensus_reached(flood_msg, threshold=0.5):
    return flood_msg["probability"] >= threshold
