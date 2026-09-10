const { searchResources, getResource } = require("../../.agents/skills/msw-search/scripts/msw_resource_api.cjs");

const candidates = [
  ["Mu Lung", "Straw Target Dummy"],
  ["Mu Lung", "Wooden Target Dummy"],
  ["Mu Lung", "Peach Monkey"],
  ["Mu Lung", "Blue Flower Serpent"],
  ["Mu Lung", "Tae Roon"],
  ["Mu Lung", "King Sage Cat"],
  ["Minar Forest", "Harp"],
  ["Minar Forest", "Blood Harp"],
  ["Minar Forest", "Blue Wyvern"],
  ["Minar Forest", "Dark Wyvern"],
  ["Minar Forest", "Manon"],
  ["Minar Forest", "Griffey"],
  ["Temple of Time", "Memory Monk Trainee"],
  ["Temple of Time", "Memory Monk"],
  ["Temple of Time", "Memory Guardian"],
  ["Temple of Time", "Chief Memory Guardian"],
  ["Temple of Time", "Dodo"],
  ["Omega Sector", "Mateon"],
  ["Omega Sector", "Plateon"],
  ["Omega Sector", "Mecateon"],
  ["Omega Sector", "Chief Gray"],
  ["Omega Sector", "Zeno"],
];

const selectedPacks = [
  ["Mu Lung", "mob/5120503.img"], ["Mu Lung", "mob/5120504.img"],
  ["Mu Lung", "mob/6130207.img"], ["Mu Lung", "mob/4230503.img"],
  ["Mu Lung", "mob/7220000.img"],
  ["Minar Forest", "mob/8140001.img"], ["Minar Forest", "mob/8140002.img"],
  ["Minar Forest", "mob/8150301.img"], ["Minar Forest", "mob/8150302.img"],
  ["Minar Forest", "mob/2600022.img"],
  ["Temple of Time", "mob/8200001.img"], ["Temple of Time", "mob/8200002.img"],
  ["Temple of Time", "mob/8200003.img"], ["Temple of Time", "mob/8200004.img"],
  ["Temple of Time", "mob/8220004.img"],
  ["Omega Sector", "mob/4230119.img"], ["Omega Sector", "mob/4230120.img"],
  ["Omega Sector", "mob/4230121.img"], ["Omega Sector", "mob/4240000.img"],
  ["Omega Sector", "mob/6220001.img"],
];

async function searchOne([area, query]) {
  try {
    const response = await searchResources(query, {
      resourceTypeFilter: ["resource_pack"],
      categoryFilter: ["mob"],
      topK: 3,
    });
    return {
      area,
      query,
      results: (response.results || []).map((entry) => ({
        id: entry.id,
        names: entry.names,
        score: entry.score,
      })),
    };
  } catch (error) {
    return { area, query, error: String(error) };
  }
}

async function main() {
  if (process.argv[2] === "compact") {
    const output = [];
    for (let i = 0; i < selectedPacks.length; i += 4) {
      output.push(...await Promise.all(selectedPacks.slice(i, i + 4).map(async ([area, id]) => {
        try {
          const pack = await getResource(id);
          return {
            area,
            id,
            names: pack.names,
            elements: Object.fromEntries((pack.payload?.elements || [])
              .filter((entry) => /(^|\/)(stand|move|jump|attack\d*|skill\d*|hit\d*|die\d*|ball|effect\d*|areaWarning)(\/|$)/i.test(entry.rel_path || ""))
              .map((entry) => [entry.rel_path, entry.ruid])),
          };
        } catch (error) {
          return { area, id, error: String(error) };
        }
      })));
    }
    console.log(JSON.stringify(output, null, 2));
    return;
  }
  if (process.argv[2] === "details") {
    const output = [];
    for (let i = 0; i < selectedPacks.length; i += 4) {
      output.push(...await Promise.all(selectedPacks.slice(i, i + 4).map(async ([area, id]) => {
        try {
          const pack = await getResource(id);
          return {
            area,
            id,
            names: pack.names,
            elements: (pack.payload?.elements || []).map((entry) => ({
              path: entry.rel_path,
              type: entry.resource_type,
              ruid: entry.ruid,
              width: entry.payload?.width,
              height: entry.payload?.height,
            })),
          };
        } catch (error) {
          return { area, id, error: String(error) };
        }
      })));
    }
    console.log(JSON.stringify(output, null, 2));
    return;
  }
  const output = [];
  for (let i = 0; i < candidates.length; i += 4) {
    output.push(...await Promise.all(candidates.slice(i, i + 4).map(searchOne)));
  }
  console.log(JSON.stringify(output, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
