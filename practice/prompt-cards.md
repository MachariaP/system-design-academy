# System Design Prompt Cards

15 prompts separated by `---`. Use with interview-simulator.md or solo practice.

---

## 1. URL Shortener 🟢

Design a URL shortening service like TinyURL.

**Constraints:** 100M DAU, 10M new short URLs/day, redirect latency < 100ms p99, 5-year data retention. Read-heavy (100:1 read-to-write ratio). Must support custom aliases and expiration.

---

## 2. WhatsApp Chat 🟡

Design a real-time messaging system like WhatsApp.

**Constraints:** 2B DAU, 100B messages/day, 1:1 and group chats (up to 256 users), media sharing (images/video/audio), delivery receipts, last-seen. End-to-end encryption requirement. Messages must arrive in < 500ms p99.

---

## 3. Uber Ride-Hailing 🟡

Design a ride-hailing platform like Uber.

**Constraints:** 100M DAU, 15M trips/day, 5M active drivers at peak. Real-time location updates every 3 seconds. Rider expects driver ETA < 10s to compute. Trip matching takes < 2s. Surge pricing during peak.

---

## 4. YouTube 🟠

Design a video streaming platform like YouTube.

**Constraints:** 2B MAU, 500 hours of video uploaded/minute, 1B hours of watch time/day. p99 video start latency < 2s. 4K support. Adaptive bitrate streaming. Comments, likes, subscriptions.

---

## 5. Netflix 🟠

Design a content streaming service like Netflix.

**Constraints:** 250M subscribers, 1B hours streamed/month. Catalog of 20K+ titles. p99 start latency < 1.5s. Multi-device support, offline downloads, personalized recommendations, multiple profiles per account.

---

## 6. Twitter Timeline 🟡

Design a social network timeline system like Twitter.

**Constraints:** 500M DAU, 500M tweets/day, average user has 200 followers, celebrities with 100M+ followers. Timeline load latency < 500ms p99. Home timeline shows tweets from followed users in reverse chronological order.

---

## 7. Web Crawler 🟢

Design a web crawler for a search engine.

**Constraints:** Crawl 10B pages/month. Respect robots.txt. Detect and avoid traps. Handle duplicates (near-identical pages). Freshness: recrawl popular pages every 15 min, others every 30 days. Storage of 100PB+.

---

## 8. Rate Limiter 🟢

Design a distributed rate limiter.

**Constraints:** 10M API calls/min peak, 100K unique API keys. Enforce per-key + per-endpoint limits. Bursts up to 2x allowed. Added latency < 5ms per check. Must work across multiple data centers.

---

## 9. Google Docs 🟠

Design a real-time collaborative document editing service like Google Docs.

**Constraints:** 1B users, 500M documents. Real-time collaboration (10+ concurrent editors). Cursor presence, comments, suggestions mode. Conflict resolution via OT/CRDT. Auto-save every 500ms.

---

## 10. Distributed KV Store 🟠

Design a distributed key-value store like DynamoDB.

**Constraints:** 10M requests/sec, multi-region, single-digit millisecond latency p99. Eventual consistency (AP) with optional strong consistency (CP). Support for both document and key-value access patterns. Auto-scaling with no downtime.

---

## 11. Real-Time Leaderboard 🟡

Design a real-time gaming leaderboard.

**Constraints:** 100M players, 10M concurrent. Scores update every game completion (~5 min/game). Leaderboard refreshes < 1s. Global + friend + regional views. Top 100, rank around me, percentile distribution.

---

## 12. Dropbox File Storage 🟡

Design a cloud file storage service like Dropbox.

**Constraints:** 500M users, 10GB average storage per user. File sync across devices. Version history (30-day retention). Large file support (10GB+). Conflict resolution for concurrent edits. Delta sync for efficiency.

---

## 13. Live Comments 🟢

Design a live comments system for a streaming platform.

**Constraints:** 10M concurrent viewers, 100K comments/sec during peak events. Comments appear < 200ms p99. Rate limiting per user. Moderation (auto-flag profanity/spam). Persistent with scrollback.

---

## 14. Distributed ID Generator 🟢

Design a distributed unique ID generator.

**Constraints:** Generate 10M IDs/sec across multiple data centers. IDs must be roughly sortable by creation time. 64-bit IDs. Highly available (99.999%). No single point of failure. Used as primary keys for sharded databases.

---

## 15. CDN 🟡

Design a content delivery network (CDN).

**Constraints:** 500 edge PoPs worldwide. Serve static assets (images, CSS, JS, video). Cache size per PoP: 100TB. Origin offload > 90%. Latency < 50ms p99 to nearest edge. Handle cache purging within 1 minute globally.
