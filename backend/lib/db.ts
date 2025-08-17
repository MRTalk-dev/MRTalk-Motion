import { ChromaClient } from "chromadb";

const client = new ChromaClient();

export const collection = await client.getOrCreateCollection({
  name: "motions",
});

export async function addToCollection(id: string, label: string) {
  await collection.add({ ids: [id], documents: [label] });
}

export async function removeFromCollection(id: string) {
  await collection.delete({ ids: [id] });
}

export async function getFromCollection(id: string) {
  return await collection.get({ ids: [id] });
}

export async function getAllDocs() {
  return await collection.get({ include: ["documents", "metadatas"] });
}

export function filterSearchResults(
  res: Awaited<ReturnType<typeof collection.query>>,
  distanceThreshold = 1
) {
  if (!res.ids[0] || !res.documents[0]) return [];

  const filtered: { document: string; id: string; distance: number }[] = [];
  res.documents[0].forEach((doc, i) => {
    const dist = res.distances[0]![i]!;
    if (dist < distanceThreshold) {
      filtered.push({ document: doc!, id: res.ids[0]![i]!, distance: dist });
    }
  });

  return filtered;
}
