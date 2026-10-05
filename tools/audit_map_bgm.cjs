// Read-only official catalogue lookup. Does not edit maps or game code.
const api = require('../.agents/skills/msw-search/scripts/msw_resource_api.cjs');
const fs = require('node:fs');
const path = require('node:path');

async function main() {
  const resources = [];
  let offset;
  do {
    const page = await api.listResources({
      resourceTypeFilter: ['bgm'], limit: 100,
      ...(offset ? { offset } : {}),
    });
    resources.push(...page.items);
    offset = page.nextOffset;
  } while (offset);
  console.log(`Official BGM resources: ${resources.length}`);
  let next = 0;
  let done = 0;
  await Promise.all(Array.from({ length: 8 }, async () => {
    while (next < resources.length) {
      const resource = resources[next++];
      const response = await api.getResourceTags(resource.id);
      resource.sourceTags = response.tags;
      done++;
      if (done % 100 === 0) console.log(`Source metadata: ${done}/${resources.length}`);
    }
  }));
  const destination = path.join(__dirname, '../docs/reports/map-bgm-official-catalog-20261005.json');
  fs.writeFileSync(destination, JSON.stringify({
    fetchedAt: new Date().toISOString(),
    source: 'https://maplestoryworlds-resourcesearch-new.nexon.com/api',
    resources,
  }, null, 2) + '\n');
  console.log(`Saved source metadata: ${destination}`);
  const names = /헤네시스|엘리니아|페리온|지하철|커닝시티|노틸러스|슬리피우드|오르비스|엘나스|아쿠아로드|에오스탑|루디브리엄|아리안트|마가티아|무릉|리프레|추억의 길|로스웰|기사단|버섯마을|사우스페리|피아누스/;
  for (const r of resources) {
    const tags = r.sourceTags;
    const matches = (tags.ko || []).filter(n => names.test(n));
    if (matches.length) console.log(JSON.stringify({
      id: r.id, path: tags.path, track: tags.subPath,
      maps: matches.slice(0, 6), length: r.payload.length,
    }));
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
