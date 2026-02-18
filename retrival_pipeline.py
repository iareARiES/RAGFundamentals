try: 
        existing_count = vectorstore._collection.count()
    except Exception:
        exixting_count = 0;
        
    total = len(chunks)
    print(f"Already embedded: {existing_count}/{total}")
    
    #Start from where we stopped
    start_i = existing_count
    i = existing_count
    
    MAX_REQUESTS_PER_MINUTE = 100
    request_count = 0
    minute_start = time.time()

    total = len(chunks)
    i = 0
    

    while i < total:
        # reset each minute
        elapsed = time.time() - minute_start
        if elapsed >= 60:
            request_count = 0
            minute_start = time.time()
            elapsed = 0

        # if hit 100 requests, wait for next minute window
        if request_count >= MAX_REQUESTS_PER_MINUTE:
            sleep_for = 60 - elapsed
            print(f"⏳ 100/min hit. Sleeping {sleep_for:.1f}s...")
            time.sleep(max(0, sleep_for))
            request_count = 0
            minute_start = time.time()

        chunk = chunks[i]

        try:
            # 1 chunk = 1 request (safe, slower)
            chunk_id = f"chunk_{i}"
            
            vectorstore.add_texts(
                texts=[chunk.page_content],
                metadatas=[chunk.metadata],
                ids =[chunk_id]
            )
            request_count += 1
            i += 1

            if i % 25 == 0 or i == total:
                print(f"✅ Embedded {i}/{total}")

        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                # obey server hint: it says retryDelay ~37s
                wait = 40 + random.uniform(0, 5)
                print(f"⚠️ 429 rate limited. Sleeping {wait:.1f}s then retry...")
                time.sleep(wait)
            else:
                raise
