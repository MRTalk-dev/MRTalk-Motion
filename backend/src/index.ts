import { randomUUIDv7 } from "bun";
import { Hono } from "hono";
import { validator } from "hono/validator";
import z from "zod";
import { collection } from "../lib";
import { serveStatic } from "hono/bun";

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

app
  .get("/docs", async (c) => {
    try {
      const docs = await collection.get({
        include: ["documents", "metadatas"],
      });
      const res = docs.ids.map((id, i) => {
        return { id, doc: docs.documents[i] };
      });
      return c.json(res);
    } catch (e) {
      return c.json({
        error: "ファイルをアップロード中にエラーが発生しました。",
      });
    }
  })
  .post(
    "/docs",
    validator("form", (value, c) => {
      const parsed = AddSchema.safeParse(value);
      if (!parsed.success) {
        return c.text("Invalid Body.", 401);
      }
      return parsed.data;
    }),
    async (c) => {
      try {
        const body = c.req.valid("form");

        const filesArray = Array.isArray(body.files)
          ? body.files
          : [body.files];

        await Promise.all(
          filesArray.map(async (file) => {
            const id = randomUUIDv7();
            const arrayBuffer = await file.arrayBuffer();
            const buf = Buffer.from(arrayBuffer);

            let extension = "";
            if (file.name.toLowerCase().endsWith(".fbx")) {
              extension = "fbx";
            } else {
              throw new Error("不正な拡張子です。");
            }

            const path = `motions/${id}.${extension}`;
            await Bun.write(path, buf);
            collection.add({ ids: [id], documents: [body.label] });
          })
        );

        return c.json({
          message: "モーションが正常に追加されました。",
        });
      } catch (e) {
        return c.json({
          error: "ファイルをアップロード中にエラーが発生しました。",
        });
      }
    }
  )
  .delete(
    "/docs",
    validator("json", (value, c) => {
      const parsed = DeleteSchema.safeParse(value);
      if (!parsed.success) {
        return c.text("Invalid Body.", 401);
      }
      return parsed.data;
    }),
    async (c) => {
      try {
        const body = c.req.valid("json");

        await collection.delete({ ids: [body.id] });

        return c.json({
          message: "モーションが正常に削除されました。",
        });
      } catch (e) {
        return c.json({
          error: "モーションを削除中にエラーが発生しました。",
        });
      }
    }
  );

app.get(
  "/search",
  validator("query", (value, c) => {
    const parsed = SearchSchema.safeParse(value);
    if (!parsed.success) {
      return c.text("Invalid Query.", 401);
    }
    return parsed.data;
  }),
  async (c) => {
    try {
      const body = c.req.valid("query");

      const res = await collection.query({ queryTexts: [body.query] });

      if (!res.ids[0] || !res.documents[0]) {
        return c.json({
          error: "モーションが見つかりませんでした。",
        });
      } else {
        const distanceThreshold = 1;

        const filtered: {
          document: string;
          id: string;
          distance: number;
        }[] = [];

        res.documents[0].forEach((doc, i) => {
          const dist = res.distances[0]![i]!;
          if (dist < distanceThreshold) {
            filtered.push({
              document: doc!,
              id: res.ids[0]![i]!,
              distance: dist,
            });
          }
        });

        if (filtered.length <= 0) {
          return c.json({
            error: "モーションが見つかりませんでした。",
          });
        } else {
          return c.json({
            id: filtered[0],
          });
        }
      }
    } catch (e) {
      return c.json({
        error: "検索中にエラーが発生しました。",
      });
    }
  }
);

app.use("/motions/*", serveStatic({ root: "./" }));

export default app;
