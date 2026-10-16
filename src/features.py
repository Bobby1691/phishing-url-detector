def extract_features(url):
    features = {}

    features["url_length"] = len(url)

    features["has_https"] = 1 if url.startswith("https") else 0

    features["special_chars"] = 0
    for ch in url:
        if not ch.isalnum():
            features["special_chars"] += 1

    words = ["login", "verify", "account", "secure", "update"]
    features["has_suspicious_word"] = 0
    for w in words:
        if w in url.lower():
            features["has_suspicious_word"] = 1

    return features


if __name__ == "__main__":
    print(extract_features("http://secure-login-verify.com"))
