/**
 * promptfoo_assertions.js - VAMOS EA 추출 프롬프트 커스텀 검증 로직 (B-12)
 * Promptfoo의 javascript assertion에서 file:// 로 참조하여 사용.
 *
 * Usage in promptfoo_config.yaml:
 *   assert:
 *     - type: javascript
 *       value: "file://D:/VAMOS/.claude/hooks/promptfoo_assertions.js:functionName"
 */

/**
 * EA JSON 스키마 기본 검증
 * 필수 필드(metadata, items)가 존재하는지 확인
 */
function assertValidEASchema(output) {
  try {
    const parsed = typeof output === 'string' ? JSON.parse(output) : output;

    if (!parsed.metadata) {
      return { pass: false, score: 0, reason: 'Missing metadata field' };
    }
    if (!parsed.items || !Array.isArray(parsed.items)) {
      return { pass: false, score: 0, reason: 'Missing or invalid items array' };
    }
    if (!parsed.metadata.source_file) {
      return { pass: false, score: 0.5, reason: 'Missing metadata.source_file' };
    }
    if (typeof parsed.metadata.total_items_extracted !== 'number') {
      return { pass: false, score: 0.5, reason: 'Missing or invalid total_items_extracted' };
    }

    return { pass: true, score: 1.0, reason: 'Valid EA schema' };
  } catch (e) {
    return { pass: false, score: 0, reason: `JSON parse error: ${e.message}` };
  }
}

/**
 * COUNT ↔ LIST 교차 검증
 * COUNT 키의 값이 관련 LIST 키의 길이와 일치하는지 확인
 */
function assertCountMatchesList(output) {
  try {
    const parsed = typeof output === 'string' ? JSON.parse(output) : output;
    const items = parsed.items || [];

    const keyMap = {};
    for (const item of items) {
      if (item.key) keyMap[item.key] = item;
    }

    const countKeys = Object.keys(keyMap).filter(k =>
      k.toUpperCase().includes('COUNT') ||
      k.toUpperCase().includes('TOTAL') ||
      k.toUpperCase().startsWith('NUM_')
    );

    const listKeys = Object.keys(keyMap).filter(k =>
      Array.isArray(keyMap[k].value)
    );

    let violations = 0;
    let checked = 0;

    for (const ck of countKeys) {
      const countVal = keyMap[ck].value;
      if (typeof countVal !== 'number') continue;

      const base = ck.toUpperCase()
        .replace('_COUNT', '').replace('_TOTAL', '')
        .replace('TOTAL_', '').replace('NUM_', '');

      for (const lk of listKeys) {
        if (base && lk.toUpperCase().includes(base)) {
          checked++;
          if (countVal !== keyMap[lk].value.length) {
            violations++;
          }
        }
      }
    }

    if (checked === 0) {
      return { pass: true, score: 0.5, reason: 'No COUNT/LIST pairs found to verify' };
    }

    const score = 1.0 - (violations / checked);
    return {
      pass: violations === 0,
      score,
      reason: violations === 0
        ? `All ${checked} COUNT/LIST pairs match`
        : `${violations}/${checked} COUNT/LIST pairs mismatch`
    };
  } catch (e) {
    return { pass: false, score: 0, reason: `Error: ${e.message}` };
  }
}

/**
 * 카테고리 분포 균형 검증
 * C1~C8 카테고리가 골고루 추출되었는지 확인
 */
function assertCategoryBalance(output) {
  try {
    const parsed = typeof output === 'string' ? JSON.parse(output) : output;
    const categories = parsed.metadata?.categories || {};

    const catValues = Object.values(categories).filter(v => typeof v === 'number' && v > 0);
    if (catValues.length < 2) {
      return { pass: false, score: 0.3, reason: 'Less than 2 categories with items' };
    }

    const total = catValues.reduce((a, b) => a + b, 0);
    const proportions = catValues.map(v => v / total);

    // Entropy-based balance
    const entropy = -proportions.reduce((acc, p) => acc + (p > 0 ? p * Math.log2(p) : 0), 0);
    const maxEntropy = Math.log2(catValues.length);
    const balance = maxEntropy > 0 ? entropy / maxEntropy : 0;

    return {
      pass: balance >= 0.5,
      score: balance,
      reason: `Category balance: ${(balance * 100).toFixed(1)}% (${catValues.length} categories)`
    };
  } catch (e) {
    return { pass: false, score: 0, reason: `Error: ${e.message}` };
  }
}

/**
 * 항목 완전성 검증
 * 각 item에 필수 필드(item_id, key, value, source_line, source_text)가 있는지 확인
 */
function assertItemCompleteness(output) {
  try {
    const parsed = typeof output === 'string' ? JSON.parse(output) : output;
    const items = parsed.items || [];

    if (items.length === 0) {
      return { pass: false, score: 0, reason: 'No items extracted' };
    }

    const required = ['item_id', 'key', 'value', 'source_line', 'source_text'];
    let incomplete = 0;

    for (const item of items) {
      for (const field of required) {
        if (item[field] === undefined || item[field] === null) {
          incomplete++;
          break;
        }
      }
    }

    const score = 1.0 - (incomplete / items.length);
    return {
      pass: incomplete === 0,
      score,
      reason: incomplete === 0
        ? `All ${items.length} items have required fields`
        : `${incomplete}/${items.length} items missing required fields`
    };
  } catch (e) {
    return { pass: false, score: 0, reason: `Error: ${e.message}` };
  }
}

/**
 * 빈 문서 처리 검증
 * 빈 입력에 대해 에러 없이 빈 결과를 반환하는지 확인
 */
function assertEmptyHandled(output) {
  try {
    // Empty input should not crash
    if (!output || output.trim() === '') {
      return { pass: true, score: 1.0, reason: 'Empty input handled gracefully (empty output)' };
    }

    const parsed = typeof output === 'string' ? JSON.parse(output) : output;
    const items = parsed.items || [];

    return {
      pass: items.length === 0,
      score: items.length === 0 ? 1.0 : 0.5,
      reason: items.length === 0
        ? 'Empty input correctly yields 0 items'
        : `Empty input yielded ${items.length} items (possible hallucination)`
    };
  } catch (e) {
    // Parse error on empty input is acceptable
    return { pass: true, score: 0.8, reason: 'Empty input handled (non-JSON response)' };
  }
}

/**
 * 회귀 테스트: 이전 결과 대비 품질 저하 여부 확인
 */
function assertNoRegression(output, context) {
  try {
    const parsed = typeof output === 'string' ? JSON.parse(output) : output;
    const currentCount = (parsed.items || []).length;

    // context.vars.previous_count가 있으면 비교
    const previousCount = context?.vars?.previous_count;
    if (previousCount !== undefined) {
      const threshold = previousCount * 0.9; // 10% 이상 감소면 regression
      if (currentCount < threshold) {
        return {
          pass: false,
          score: currentCount / previousCount,
          reason: `Regression: ${currentCount} items (was ${previousCount}, threshold ${Math.ceil(threshold)})`
        };
      }
    }

    return {
      pass: true,
      score: 1.0,
      reason: `${currentCount} items extracted (no regression detected)`
    };
  } catch (e) {
    return { pass: false, score: 0, reason: `Error: ${e.message}` };
  }
}

// Export functions for promptfoo
module.exports = {
  assertValidEASchema,
  assertCountMatchesList,
  assertCategoryBalance,
  assertItemCompleteness,
  assertEmptyHandled,
  assertNoRegression,
};
