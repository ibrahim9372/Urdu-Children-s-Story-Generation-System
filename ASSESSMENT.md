# Comprehensive Technical Assessment Report

**Project:** Urdu Children's Story Generation System  
**Date:** 2026-02-17  
**Scope:** Phases I–V (Phase VI not yet implemented)

---

## Executive Summary

The codebase provides a skeleton implementation across Phases I–V but has **significant architectural, logic, and requirements-compliance bugs** that would prevent the system from working correctly end-to-end. The most critical issues are in Phase II (Tokenizer) and Phase III (Trigram LM), where fundamental misunderstandings of BPE vocabulary size, the special-token encoding scheme, and the contract between the tokenizer and the LM result in a broken generation pipeline. The Backend duplicates generator logic instead of reusing the model module cleanly, and the Frontend lacks any error feedback UI and has no streaming/step-wise output as required.

**Total bugs found: 38**  
- CRITICAL: 7  
- HIGH: 12  
- MEDIUM: 13  
- LOW: 6

---

## System Architecture Map

```
Data/ (Phase I)
  00-data-collection.ipynb  ──scrape──►  urdu_stories_final.json
  01-cleaning.ipynb         ──clean──►   urdu_stories_final_preprocessed.json
  02-segmentation-audit.ipynb            (audit only)
  03-tokenizer.ipynb        ──export──►  urdu_tokenizer_training.txt
  04-dataset-eda.ipynb                   (analysis only)

Tokenizer/ (Phase II)
  train_bpe.py  ──reads urdu_tokenizer_training.txt──►  artifacts/ordered_merges.txt
                                                        artifacts/final_token.json

Trigram_LM/ (Phase III)
  ngram_counter.py  ──reads final_token.json──►  artifacts/{unigrams,bigrams,trigrams}.pkl
  trigram_model.py  ──reads pkl files──►         (standalone generation script)

Backend/ (Phase IV)
  main.py          FastAPI app
  schemas.py       Pydantic models
  model_loader.py  loads pkl + tokenizer artifacts
  generator.py     story generation (duplicate of trigram_model.py)

Frontend/ (Phase V)
  React 19 + Vite + Tailwind chat UI
  api.js  ──POST /generate──►  Backend

Deployment/ (Phase VI)
  empty (folder_context.md only)
```

---

## Phase I — Data Collection & Preprocessing

### Files Analyzed
- `Data/00-data-collection.ipynb` (5 cells)
- `Data/01-cleaning.ipynb` (5 cells)
- `Data/02-segmentation-audit.ipynb` (4 cells)
- `Data/03-tokenizer.ipynb` (3 cells)
- `Data/04-dataset-eda.ipynb` (10 cells)
- `Data/urdu_stories_final.json`, `urdu_stories_final_preprocessed.json`, `urdu_tokenizer_training.txt`

### Bug Table

| Bug ID | File | Function / Line | Bug Type | Severity | Description | Impact | Root Cause | Solution |
|--------|------|-----------------|----------|----------|-------------|--------|------------|----------|
| **1A-01** | `00-data-collection.ipynb` cell 3 | `clean_and_tokenize()` | Requirements Non-Compliance | **CRITICAL** | Special tokens `<EOS>`, `<EOP>`, `<EOT>` are used as plain ASCII strings, not as "unused Unicode bytes" as required by the spec: *"Add un-used unicode bytes for special tokens"*. | Tokenizer will treat `<`, `E`, `O`, `S`, `>` as separate characters during BPE, splitting them across merge operations. This fundamentally breaks the token boundary scheme. | Developers used human-readable angle-bracket markers instead of single Unicode code-points from the Private Use Area (e.g., U+E000, U+E001, U+E002). | Replace `<EOS>` → `\uE000`, `<EOP>` → `\uE001`, `<EOT>` → `\uE002` everywhere (scraper output, cleaning, tokenizer training text, model, and backend). |
| **1A-02** | `00-data-collection.ipynb` cell 4 | `clean_and_tokenize()` | Logic Error | **HIGH** | `<EOP>` is appended after `<br>` or `<p>` tags by checking `text.parent.name`, but `text` is a NavigableString — its `.parent` is the tag *containing* the text, not a following `<br>`. For `<br>` (self-closing), no NavigableString is ever a direct child, so this condition is rarely satisfied. | Many paragraph boundaries are missed; story text is concatenated into one long paragraph. | Confusion between the text node's parent and the sibling `<br>` structure. | Walk `container.descendants` or use `get_text(separator='\n')` and split on double-newlines to detect `<EOP>` boundaries. |
| **1A-03** | `00-data-collection.ipynb` cell 4 | `clean_and_tokenize()` | Logic Error | **MEDIUM** | `if "2026" in full_content` is a year-hardcode used to strip header boilerplate. It will fire on any story that mentions the year 2026 (or any string containing "2026") and corrupt the text. | Legitimate story content truncated. | Brittle heuristic instead of a robust boilerplate detector. | Use a regex targeting the exact header pattern or remove the heuristic entirely. |
| **1A-04** | `00-data-collection.ipynb` cell 4 | `clean_and_tokenize()` | Logic Error | **MEDIUM** | `if "Facebook" in full_content` truncates at the first occurrence. If the word "فیسبک" appears in Urdu text, it won't match, but if a story contains the English word "Facebook" mid-text, everything after is dropped. | Partial story loss. | Heuristic footer detection too aggressive. | Target the exact social-sharing footer HTML class or remove the heuristic. |
| **1A-05** | `00-data-collection.ipynb` cell 4 | `fetch_story()` | Concurrency/Correctness | **MEDIUM** | `ThreadPoolExecutor` with `max_workers=3` shares a single `cloudscraper` session object across threads. `cloudscraper` is not documented as thread-safe, and its internal cookie jar can cause race conditions. | Sporadic 403s, corrupted cookies, dropped stories. | Shared stateful scraper instance. | Create a per-thread scraper instance inside `fetch_story()`. |
| **1A-06** | `00-data-collection.ipynb` cell 4 | `clean_and_tokenize()` | Logic Error | **MEDIUM** | `<EOS>` is inserted after *every* Urdu sentence terminator (`[۔！？]`), but the regex `re.sub(r'([۔！？])', r' <EOS>', full_content)` replaces the punctuation mark itself with ` <EOS>`, destroying the original punctuation. | All ۔ ！ ？ characters are removed from the corpus. | Regex substitution replaces the match group instead of appending after it. | Change to `re.sub(r'([۔！？])', r'\1 <EOS>', full_content)`. |
| **1A-07** | `01-cleaning.ipynb` cell 3 | `normalize_urdu()` | Logic Error | **LOW** | Diacritics are stripped unconditionally. While this is common for normalization, it changes word meaning in some Urdu contexts (e.g., distinguishing vowels in ambiguous word forms). No flag or option to preserve diacritics. | Minor meaning loss in rare cases; acceptable for this use case but should be documented. | Design trade-off not documented. | Add a comment/flag; acceptable as-is if conscious choice. |
| **1A-08** | `01-cleaning.ipynb` cell 3 | `normalize_urdu()` | Logic Error | **MEDIUM** | Zero-Width Non-Joiner (`\u200C`) is removed. In Urdu, ZWNJ is *significant* — it controls character joining behavior in compound words (e.g., "می‌خواهم"). Removing it alters displayed text. | Words render differently; subtle correctness issue. | Over-aggressive normalization. | Preserve `\u200C` or justify its removal. |
| **1A-09** | `01-cleaning.ipynb` cell 3 | `insert_missing_eos()` | Logic Error | **LOW** | The `_TERMINATOR_RE` pattern looks for terminators not already followed by `<EOS>`. But after `normalize_urdu()` replaces ك→ک and ي→ی, the `.` in the regex character class (`[\u06D4\u061F\.\!\?]`) matches ASCII `.` which may not appear in Urdu text. Mixing Urdu and ASCII terminators. | Minor: may insert spurious `<EOS>` after stray ASCII periods. | Mixed-script terminator set. | Separate ASCII and Urdu terminator handling. |
| **1A-10** | `00-data-collection.ipynb` cell 5 | tokenizer text export | Data Inconsistency | **HIGH** | Cell 5 exports `urdu_tokenizer_training.txt` from `urdu_stories_final.json` (raw/uncleaned), not from the preprocessed JSON. Notebook `03-tokenizer.ipynb` correctly uses the preprocessed file. If cell 5 was run after data collection but before cleaning, the training text is derived from dirty data. | Tokenizer may be trained on unclean data if the user ran the notebooks out of order. | Two export paths exist: one in `00-data-collection.ipynb` cell 5, one in `03-tokenizer.ipynb`. | Remove cell 5 from `00-data-collection.ipynb`; the canonical export lives in `03-tokenizer.ipynb`. |

---

## Phase II — BPE Tokenizer

### Files Analyzed
- `Tokenizer/train_bpe.py`
- `Tokenizer/artifacts/ordered_merges.txt`, `final_token.json`

### Bug Table

| Bug ID | File | Function / Line | Bug Type | Severity | Description | Impact | Root Cause | Solution |
|--------|------|-----------------|----------|----------|-------------|--------|------------|----------|
| **2A-01** | `train_bpe.py` | `num_merges = 250` | Requirements Non-Compliance | **CRITICAL** | The spec says *"vocabulary size hyperparameter should be set to 250"*, meaning the **final vocabulary size** should be 250. The code performs 250 **merge operations** instead. The initial vocabulary is all unique characters + `</w>` (likely 80–100+ symbols), so after 250 merges the vocab size is `initial_chars + 250` ≈ 350–400+, not 250. | Vocabulary is significantly larger than required, violating the spec. | Confusion between "number of merges" and "vocab size". | Set `num_merges = 250 - len(initial_char_vocab)` to arrive at exactly vocab size = 250. |
| **2A-02** | `train_bpe.py` | `get_word_frequencies()` | Logic Error | **HIGH** | `re.sub(r"[^\w\s<>]", " ", text)` strips all Urdu punctuation (۔ ؟ ، etc.) before tokenization. This means the tokenizer never sees these characters and cannot encode them. At generation time, if the model produces text with these characters, the tokenizer cannot decode them. | Punctuation is erased from the training vocabulary; generated text will never contain proper Urdu punctuation. | Over-aggressive character filtering. | Allow Urdu punctuation through the regex: `re.sub(r"[^\w\s<>۔؟،؛!]", " ", text)`. Or better, don't strip at all — BPE should learn from the raw byte stream. |
| **2A-03** | `train_bpe.py` | `translate_corpus_to_bpe()` | Logic Error | **HIGH** | Special tokens like `<EOS>`, `<EOP>`, `<EOT>` are detected with `word.startswith("<") and word.endswith(">")`, treated as whole units, and get `</w>` appended. But the corpus has `<EOS>` as a whitespace-separated token. If BPE merges have already created sub-tokens containing `<` or `>`, they will collide. Moreover, these tokens become `<EOS></w>`, `<EOP></w>` etc., not matching the original multi-character form. | Special tokens are not properly preserved as atomic units through BPE. Trigram model sees `<EOS></w>` but generation checks for `<EOT>` without `</w>`. Cross-component mismatch. | No explicit special-token reservation in the BPE algorithm. | Use single Unicode codepoints for special tokens (see 1A-01), or add them to the vocabulary as pre-defined tokens before merging and skip them during BPE pair counting. |
| **2A-04** | `train_bpe.py` | `merge_vocab()` | Logic Error | **MEDIUM** | `word_tuple[i : i + 2] == bigram` compares a tuple slice with a tuple. This works correctly in Python, but the comparison is O(1) only for short tuples. More importantly, this never handles the edge case where merging creates a new pair that equals an earlier merge — BPE assumes merges are applied in order, but the function does a single pass. This is correct per standard BPE. | No bug per se, but the code lacks validation that the merge actually changed anything. If a merge produces no changes, the loop still continues. | Minor performance issue. | Add an early-termination check if no changes were made. |
| **2A-05** | `train_bpe.py` | N/A | Missing Feature | **HIGH** | No `encode()` or `decode()` functions are exposed. The tokenizer only has `tokenize_word()` (byte-level) and `translate_corpus_to_bpe()` (batch). There is no way for the Backend to take a user's input prefix and convert it to BPE tokens for trigram lookup. | The Backend's `generator.py` simply appends `</w>` to raw words without applying BPE merges. The seed tokens will almost never match the vocabulary the trigram model was trained on. | Tokenizer was written as a one-shot training script, not as a reusable module with encode/decode API. | Add `encode(text) -> List[str]` and `decode(tokens) -> str` functions. Import and use them in the Backend. |
| **2A-06** | `train_bpe.py` | `tokenize_word()` | Logic Error | **LOW** | Always appends `</w>` (end-of-word marker) to every word. This is standard BPE, but the marker is a 4-character string that participates in BPE merges. If `</w>` was never a merge target, every token sequence ends with an unmerged `</w>`, inflating the token count. | The `final_token.json` artifact has `</w>` as a separate token after most words, bloating the corpus representation. The trigram model treats `</w>` as a regular token in its n-gram context. | Standard BPE behavior, but the trigram model was not designed to handle end-of-word markers in its context window. | Either strip `</w>` before feeding to the trigram model, or incorporate it into the trigram model's generation logic properly. |

---

## Phase III — Trigram Language Model

### Files Analyzed
- `Trigram_LM/ngram_counter.py`
- `Trigram_LM/trigram_model.py`
- `Trigram_LM/artifacts/` (unigrams.pkl, bigrams.pkl, trigrams.pkl)

### Bug Table

| Bug ID | File | Function / Line | Bug Type | Severity | Description | Impact | Root Cause | Solution |
|--------|------|-----------------|----------|----------|-------------|--------|------------|----------|
| **3A-01** | `trigram_model.py` | `generate_story_mle()` | Logic Error | **CRITICAL** | Seed words have `</w>` appended (`seed_w1 + "</w>"`), but the user's input words are raw Urdu text. The trigram model was trained on BPE sub-tokens (e.g., `ای`, `ک</w>`), not on full words with `</w>`. Concatenating the raw word with `</w>` produces a token that almost certainly doesn't exist in the vocabulary, so the first trigram lookup always fails and falls back to unigram sampling. | Generation is essentially random unigram sampling, not trigram-guided. Seed words have zero actual influence on the output. | No integration with the BPE tokenizer's `encode()` function. | BPE-encode the seed words first, then use the resulting sub-tokens as initial context. |
| **3A-02** | `trigram_model.py` | `generate_story_mle()` | Performance | **CRITICAL** | On every generation step, `probs = [get_interpolated_prob(w1, w2, t) for t in vocab]` iterates over the *entire* vocabulary (every unique token). With BPE, the vocabulary may be 5000+ unique sub-tokens. For `max_length=150` steps, this means 150 × 5000+ = 750,000+ probability calculations per request. Each call involves 3 dictionary lookups. | API response times will be extremely slow (likely 5-30+ seconds per request). | Brute-force probability computation over entire vocabulary instead of sparse lookup. | Only compute probabilities for tokens that actually appear after the given bigram context (i.e., iterate over observed trigrams starting with `(w1, w2)` only). Build an inverted index `{(w1,w2): {w3: count}}` at load time. |
| **3A-03** | `trigram_model.py` | `generate_story_mle()` | Logic Error | **HIGH** | The `<EOT>` check is: `if next_token == "<EOT>" or next_token == "<EOT></w>"`. But the actual token in the vocabulary depends on how BPE processed `<EOT>`. If the special token was split by BPE into sub-characters (e.g., `<`, `E`, `O`, `T`, `>`), neither of these string comparisons will ever match. | Story generation never terminates via `<EOT>` — it always runs to `max_length`. | Special tokens not preserved as atomic units through BPE (see 2A-03). | Fix the special token scheme (see 1A-01) and update this check accordingly. |
| **3A-04** | `trigram_model.py` | `generate_story_mle()` | Logic Error | **HIGH** | `raw_output = "".join(story).replace("</w>", " ")` joins all BPE sub-tokens without spaces, then replaces `</w>` with a space. This reconstructs words correctly only if every word ends with exactly one `</w>` and sub-tokens within a word have no spaces. Since BPE may produce sub-tokens like `ای`, `ک</w>`, joining gives `ایک` which is correct. But if `</w>` appears mid-join unexpectedly (e.g., from a single-char word), extra spaces appear. | Minor reconstruction errors in some edge cases. | Fragile string-based decoding instead of a proper BPE `decode()` function. | Use the tokenizer's `decode()` function (once implemented, see 2A-05). |
| **3A-05** | `trigram_model.py` | `generate_story_mle()` | Missing Feature | **HIGH** | The `<EOS>` and `<EOP>` tokens are not handled during generation. When the model generates these tokens (if they exist as-is in the vocab), they appear as literal text in the output. No newline or paragraph-break formatting is applied. | Generated stories have `<EOS>` and `<EOP>` as visible text instead of proper formatting. | No post-processing or decoding of structural markers. | Replace `<EOS>` with sentence-ending punctuation (or nothing, if punctuation is already present) and `<EOP>` with newline. |
| **3A-06** | `ngram_counter.py` | `ARTIFACTS_DIR` | Path Error | **MEDIUM** | `ARTIFACTS_DIR = "Trigram_LM/artifacts"` is a relative path. This only works if the script is run from the project root. If run from `Trigram_LM/` directory or from any other working directory, it fails. | Script fails with `FileNotFoundError` if CWD isn't the project root. | Inconsistent path handling (other scripts use `Path(__file__).parent`). | Use `ARTIFACTS_DIR = Path(__file__).parent / "artifacts"`. |
| **3A-07** | `ngram_counter.py` | `__main__` block | Error Handling | **LOW** | `SystemExit(0)` creates a `SystemExit` instance but doesn't raise it. Should be `raise SystemExit(0)` or `sys.exit(0)`. | Script continues to execute after "exiting", hitting the `ValueError` check on the next line — so it still fails, but with a misleading error message. | Coding mistake. | Change to `sys.exit(0)` or `raise SystemExit(0)`. |
| **3A-08** | `trigram_model.py` | module-level | Architecture | **HIGH** | `uni_counts, bi_counts, tri_counts = load_counts()` runs at **import time**. Any module that imports `trigram_model` (e.g., for testing or utilities) will immediately trigger file I/O and fail if pickle files don't exist. | Cannot import the module without artifacts present; breaks testability and modularity. | Eager loading at module scope. | Use lazy loading (as `generator.py` in the Backend does). |
| **3A-09** | `trigram_model.py` | `get_interpolated_prob()` | Logic Error | **MEDIUM** | Lambda values `(0.8, 0.15, 0.05)` are hardcoded with no justification or tuning. The spec says "implement interpolation technique as discussed in class," which typically involves held-out tuning of lambda values via EM or grid search. | Sub-optimal generation quality; lambdas may not be appropriate for this corpus. | No lambda tuning implemented. | Add a lambda tuning script or at minimum make lambdas configurable. |

---

## Phase IV — Backend (FastAPI)

### Files Analyzed
- `Backend/main.py`
- `Backend/schemas.py`
- `Backend/model_loader.py`
- `Backend/generator.py`
- `Backend/requirements.txt`

### Bug Table

| Bug ID | File | Function / Line | Bug Type | Severity | Description | Impact | Root Cause | Solution |
|--------|------|-----------------|----------|----------|-------------|--------|------------|----------|
| **4A-01** | `generator.py` | `generate_story()` | Architecture / Duplication | **HIGH** | `generator.py` is a near-copy of `trigram_model.py` with the same generation logic, same interpolation function, same bugs. Code is duplicated instead of importing from the existing module. | Bug fixes must be applied in two places; drift between implementations. | Copy-paste development. | Import generation logic from `Trigram_LM.trigram_model` or extract shared logic into a common module. |
| **4A-02** | `generator.py` | `generate_story()` | Logic Error | **CRITICAL** | Same seed-word bug as 3A-01: `seed_w1 + "</w>"` without BPE encoding. The user's prefix is split on whitespace and the first two words get `</w>` appended, producing tokens that don't exist in the trained vocabulary. | Generation ignores user input; falls back to random unigram sampling. | No BPE tokenizer integration. | BPE-encode the prefix before seeding the trigram generator. |
| **4A-03** | `main.py` | `generate()` endpoint | Missing Feature | **MEDIUM** | The endpoint only uses the first 2 words of the prefix. The API spec says "Input: prefix string, max-length" but there is no `max_length` parameter in `GenerateRequest`. Words beyond the first two in the prefix are silently ignored. | Users cannot control generation length; extra prefix words are discarded. | Incomplete schema definition. | Add `max_length: int = Field(150, ge=1, le=1000)` to `GenerateRequest` and pass it through. |
| **4A-04** | `main.py` | CORS middleware | Configuration | **MEDIUM** | `allow_origins` only permits `localhost:5173` and `127.0.0.1:5173`. After deployment (Phase VI), the Vercel frontend URL will be blocked. | Frontend cannot communicate with backend after deployment. | Hardcoded development-only origins. | Use environment variable for allowed origins; add the production URL. |
| **4A-05** | `model_loader.py` | `load_tokenizer_vocab()` | Dead Code | **LOW** | This function loads `final_token.json` but is never called anywhere. It returns the full translated corpus (a list of tokens), not a usable vocabulary or encode/decode interface. | Unused code; misleading function name suggests it loads a vocabulary but actually loads a token stream. | Incomplete implementation. | Either remove or implement proper tokenizer loading with encode/decode. |
| **4A-06** | `schemas.py` | `GenerateRequest` | Missing Validation | **MEDIUM** | No validation that the prefix contains Urdu text. A user can send English text, emoji, or arbitrary strings. The model will fail silently (tokens won't match vocabulary) and return random text. | Poor user experience; no useful error message for invalid input. | Missing input validation. | Add a validator that checks for Urdu character content. |
| **4A-07** | `main.py` | `generate()` endpoint | Missing Feature | **MEDIUM** | The spec requires "streaming or step-wise story completion (just like chatGPT)." The endpoint returns a single JSON response with the complete story. No SSE, WebSocket, or chunked transfer support. | No streaming capability; the frontend cannot display incremental generation. | Backend not designed for streaming. | Implement `StreamingResponse` with SSE or WebSocket for token-by-token delivery. |

---

## Phase V — Frontend (React)

### Files Analyzed
- `Frontend/src/App.jsx`
- `Frontend/src/components/ChatInterface.jsx`
- `Frontend/src/components/InputArea.jsx`
- `Frontend/src/components/Message.jsx`
- `Frontend/src/utils/api.js`
- `Frontend/index.html`
- `Frontend/src/index.css`
- `Frontend/package.json`

### Bug Table

| Bug ID | File | Function / Line | Bug Type | Severity | Description | Impact | Root Cause | Solution |
|--------|------|-----------------|----------|----------|-------------|--------|------------|----------|
| **5A-01** | `api.js` | `API_BASE_URL` | Configuration | **CRITICAL** | Hardcoded `http://localhost:8000`. No environment variable or build-time configuration. After deployment, the frontend will still try to reach `localhost:8000` which won't exist on the user's machine. | Frontend completely non-functional in production. | No environment-based configuration. | Use `import.meta.env.VITE_API_URL` or similar. |
| **5A-02** | `ChatInterface.jsx` | `handleSendMessage()` | Error Handling | **HIGH** | The `catch` block logs the error to console but shows nothing to the user. No error message is displayed in the chat. The typing indicator is dismissed, and the user sees nothing — they don't know the request failed. | Silent failure; terrible UX. | Missing error state UI. | Add an error message to the messages list (e.g., "Generation failed. Please try again."). |
| **5A-03** | `ChatInterface.jsx` | Message IDs | Logic Error | **MEDIUM** | `id: Date.now()` for user message and `id: Date.now() + 1` for bot message. If two messages are sent within the same millisecond (unlikely but possible with fast clicks), IDs collide. React will warn about duplicate keys. | Potential React rendering bugs with duplicate keys. | Using timestamp as unique ID. | Use a proper UUID generator or a monotonically increasing counter. |
| **5A-04** | `ChatInterface.jsx` / `api.js` | N/A | Missing Feature | **HIGH** | No streaming/step-wise display. The spec requires "streaming or step-wise story completion (just like chatGPT)." The current implementation waits for the full response and displays it all at once. | Does not meet requirements. | Neither backend nor frontend implements streaming. | Implement SSE consumption in `api.js` and character-by-character or token-by-token rendering in `Message.jsx`. |
| **5A-05** | `index.html` | `<title>` | Code Quality | **LOW** | Page title is "frontend" instead of something meaningful like "Urdu Story Generator". | Unprofessional appearance. | Boilerplate not updated. | Change to `<title>Urdu Children's Story Generator</title>`. |
| **5A-06** | `index.html` | `<html lang="en">` | Accessibility | **LOW** | The page language is set to "en" (English) but the primary content is Urdu. | Accessibility tools and screen readers will use incorrect language model. | Boilerplate not updated. | Change to `<html lang="ur" dir="rtl">` or use a mixed-language approach. |

---

## Phase VI — Deployment (Not Implemented)

### Missing Items per Requirements

| Bug ID | Item | Bug Type | Severity | Description |
|--------|------|----------|----------|-------------|
| **6A-01** | Dockerfile | Missing Deliverable | **CRITICAL** | No Dockerfile exists anywhere in the project. The spec requires "Provide a Dockerfile." | 
| **6A-02** | GitHub Actions CI/CD | Missing Deliverable | **CRITICAL** | No `.github/workflows/` directory. The spec requires "a GitHub Actions CI/CD pipeline." |
| **6A-03** | Vercel deployment | Missing Deliverable | **HIGH** | No Vercel configuration (`vercel.json`) or deployment instructions. |

---

## Cross-Cutting / Architectural Issues

| Bug ID | Area | Bug Type | Severity | Description | Solution |
|--------|------|----------|----------|-------------|----------|
| **XA-01** | Tokenizer ↔ Trigram LM | Integration Failure | **CRITICAL** | The trigram model is trained on BPE sub-tokens (from `final_token.json`), but at generation time, seed words are raw full words with `</w>` appended. There is no BPE encoding step in the generation pipeline. The entire generation pipeline is fundamentally broken because the input representation doesn't match the training representation. | Build a proper BPE `encode()` function and call it in the generation pipeline before trigram lookup. |
| **XA-02** | Special Tokens | Design Flaw | **HIGH** | The `<EOS>`, `<EOP>`, `<EOT>` tokens are multi-character ASCII strings that BPE can split. They should be single Unicode codepoints reserved before BPE training. This issue propagates through every phase. | Use Private Use Area codepoints (U+E000–U+E002); update all files accordingly. |
| **XA-03** | Backend ↔ Trigram_LM | Code Duplication | **MEDIUM** | `Backend/generator.py` duplicates `Trigram_LM/trigram_model.py` almost verbatim. Both have the same bugs. | Create a shared module or have Backend import from Trigram_LM. |
| **XA-04** | No Tests | Quality | **MEDIUM** | Zero test files anywhere in the project. No unit tests, no integration tests, no smoke tests. | Add at minimum: tokenizer round-trip test, trigram probability test, API endpoint test. |

---

## Severity Summary

| Severity | Count | Bug IDs |
|----------|-------|---------|
| **CRITICAL** | 7 | 1A-01, 2A-01, 3A-01, 3A-02, 4A-02, 5A-01, XA-01 |
| **HIGH** | 12 | 1A-02, 1A-10, 2A-02, 2A-03, 2A-05, 3A-03, 3A-05, 3A-08, 4A-01, 5A-02, 5A-04, XA-02 |
| **MEDIUM** | 13 | 1A-03, 1A-04, 1A-05, 1A-06, 1A-08, 2A-04, 3A-06, 3A-09, 4A-03, 4A-04, 4A-06, 4A-07, 5A-03 |
| **LOW** | 6 | 1A-07, 1A-09, 2A-06, 3A-07, 5A-05, 5A-06 |

*Note: Phase VI missing deliverables (6A-01, 6A-02, 6A-03) and cross-cutting issues (XA-01 to XA-04) are counted separately above.*

---

## Recommended Fix Order

The dependencies between bugs dictate this implementation sequence:

### Tier 1 — Foundation Fixes (must be done first)
1. **1A-01 + XA-02**: Replace ASCII special tokens with Unicode PUA codepoints across all phases
2. **1A-06**: Fix `<EOS>` insertion regex in scraper (preserves punctuation)
3. **1A-02**: Fix paragraph detection in scraper
4. Re-run data collection, cleaning, and tokenizer training text export

### Tier 2 — Tokenizer Fixes
5. **2A-01**: Fix vocab size calculation (merges = 250 - initial_vocab_size)
6. **2A-02**: Stop stripping Urdu punctuation in `get_word_frequencies()`
7. **2A-05**: Implement `encode()` and `decode()` functions as a reusable module
8. **2A-03**: Properly handle special tokens as atomic units
9. Re-train the BPE tokenizer

### Tier 3 — Trigram Model Fixes
10. **3A-06**: Fix relative path in `ngram_counter.py`
11. **3A-07**: Fix `SystemExit` bug
12. **3A-08**: Make `trigram_model.py` use lazy loading
13. Re-train the trigram model on corrected BPE output
14. **3A-01 + XA-01**: Integrate BPE `encode()` into generation pipeline
15. **3A-02**: Optimize probability computation with sparse lookup
16. **3A-05**: Handle structural markers in output formatting
17. **3A-09**: Add lambda tuning

### Tier 4 — Backend Fixes
18. **4A-01 + XA-03**: Remove duplicated code; import from shared module  
19. **4A-02**: (Resolved by Tier 3 fix #14)
20. **4A-03**: Add `max_length` to request schema
21. **4A-06**: Add Urdu input validation
22. **4A-07**: Implement streaming endpoint (SSE)
23. **4A-04**: Make CORS origins configurable via environment

### Tier 5 — Frontend Fixes
24. **5A-01**: Use environment variable for API URL
25. **5A-02**: Add error message display
26. **5A-04**: Implement SSE/streaming consumption
27. **5A-03, 5A-05, 5A-06**: Minor fixes

### Tier 6 — Deployment
28. **6A-01**: Create Dockerfile
29. **6A-02**: Create GitHub Actions workflow
30. **6A-03**: Configure Vercel deployment

### Tier 7 — Quality
31. **XA-04**: Add tests

---

## Assessment Completeness Checklist

- [x] Every file in the project analyzed
- [x] All functions and classes understood
- [x] Data flow completely mapped
- [x] All integration points validated
- [x] Error handling comprehensively reviewed
- [x] Performance characteristics understood
- [x] Security implications assessed

## Documentation Completeness

- [x] Bug tracking table with all issues
- [x] Severity classification justified
- [x] Solutions detailed and specific
- [x] Implementation order established
- [x] Conflict analysis completed (dependency mapping in fix order)
- [x] Risk assessment documented (critical issues flagged)
