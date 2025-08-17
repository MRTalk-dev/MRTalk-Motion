export async function saveFile(file: File, id: string) {
  const extension = file.name.toLowerCase().endsWith(".fbx") ? "fbx" : null;
  if (!extension) throw new Error("不正な拡張子です。");

  const arrayBuffer = await file.arrayBuffer();
  const buf = Buffer.from(arrayBuffer);

  const path = `motions/${id}.${extension}`;
  await Bun.write(path, buf);
  return path;
}

export async function deleteFile(id: string) {
  const path = `motions/${id}.fbx`;
  const file = Bun.file(path);
  await file.delete();
}
