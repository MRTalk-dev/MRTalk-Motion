import { randomUUIDv7 } from "bun";
import { Hono } from "hono";
import { validator } from "hono/validator";
import z from "zod";
import {
  addToCollection,
  collection,
  getAllDocs,
  getFromCollection,
  removeFromCollection,
} from "../lib/db";
import { serveStatic } from "hono/bun";
import { logger } from "hono/logger";
import { deleteFile, saveFile } from "../lib/file";
import { cors } from "hono/cors";

const AddSchema = z.object({
  files: z.union([
    z
      .instanceof(File)
      .refine(
        (f) =>
          ["model/fbx"].includes(f.type) ||
          f.name.toLowerCase().endsWith(".fbx"),
        { message: "Only .fbx files are allowed" }
      ),
    z.array(
      z
        .instanceof(File)
        .refine(
          (f) =>
            ["model/fbx"].includes(f.type) ||
            f.name.toLowerCase().endsWith(".fbx"),
          { message: "Only .fbx files are allowed" }
        )
    ),
  ]),
  label: z.string(),
});

const DeleteSchema = z.object({
  id: z.string(),
});

const SearchSchema = z.object({
  query: z.string(),
});

const app = new Hono();
app.use(logger());
app.use("*", cors());

app.get("/docs", async (c) => {
  try {
    const docs = await getAllDocs();
    const res = docs.ids.map((id, i) => ({ id, doc: docs.documents[i] }));
    return c.json(res);
  } catch {
    return c.json({ error: "ファイルを取得中にエラーが発生しました。" });
  }
});

app.post(
  "/docs",
  validator("form", (value, c) => {
    const parsed = AddSchema.safeParse(value);
    if (!parsed.success) return c.text("Invalid Body.", 400);
    return parsed.data;
  }),
  async (c) => {
    try {
      const body = c.req.valid("form");
      const filesArray = Array.isArray(body.files) ? body.files : [body.files];

      await Promise.all(
        filesArray.map(async (file) => {
          const id = randomUUIDv7();
          await saveFile(file, id);
          await addToCollection(id, body.label);
        })
      );

      return c.json({ message: "モーションが正常に追加されました。" });
    } catch {
      return c.json({
        error: "ファイルをアップロード中にエラーが発生しました。",
      });
    }
  }
);

app.delete(
  "/docs",
  validator("json", (value, c) => {
    const parsed = DeleteSchema.safeParse(value);
    if (!parsed.success) return c.text("Invalid Body.", 400);
    return parsed.data;
  }),
  async (c) => {
    try {
      const body = c.req.valid("json");
      const doc = await getFromCollection(body.id);

      if (doc) {
        await removeFromCollection(body.id);
        await deleteFile(body.id);
        return c.json({ message: "モーションが正常に削除されました。" });
      } else {
        return c.json({ message: "モーションが見つかりませんでした。" });
      }
    } catch {
      return c.json({ error: "モーションを削除中にエラーが発生しました。" });
    }
  }
);

app.get(
  "/search",
  validator("query", (value, c) => {
    const parsed = SearchSchema.safeParse(value);
    if (!parsed.success) return c.text("Invalid Query.", 400);
    return parsed.data;
  }),
  async (c) => {
    try {
      const body = c.req.valid("query");
      const res = await collection.query({
        queryTexts: [body.query],
        nResults: 1,
      });

      if (res.ids[0]!.length <= 0) {
        return c.json({ error: "モーションが見つかりませんでした。" });
      }

      return c.json({
        id: res.ids[0]![0],
        doc: res.documents[0]![0],
        distance: res.distances[0]![0],
      });
    } catch {
      return c.json({ error: "検索中にエラーが発生しました。" });
    }
  }
);

app.use("/motions/*", serveStatic({ root: "./", mimes: { model: "fbx" } }));
app.get("/", serveStatic({ path: "./views/index.html" }));

export default app;
