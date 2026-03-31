#!/usr/bin/env node
import { authenticate } from "@google-cloud/local-auth";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "fs";
import { google } from "googleapis";
import path from "path";

const drive = google.drive("v3");
const server = new Server(
  {
    name: "gdrive-server",
    version: "0.2.0",
  },
  {
    capabilities: {
      resources: {},
      tools: {},
    },
  }
);

server.setRequestHandler(ListResourcesRequestSchema, async (request) => {
  const pageSize = 10;
  const params = {
    pageSize,
    fields: "nextPageToken, files(id, name, mimeType)",
  };
  if (request.params?.cursor) {
    params.pageToken = request.params.cursor;
  }
  const res = await drive.files.list(params);
  const files = res.data.files;
  return {
    resources: files.map((file) => ({
      uri: `gdrive:///${file.id}`,
      mimeType: file.mimeType,
      name: file.name,
    })),
    nextCursor: res.data.nextPageToken,
  };
});

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const fileId = request.params.uri.replace("gdrive:///", "");
  const file = await drive.files.get({
    fileId,
    fields: "mimeType",
  });
  if (file.data.mimeType?.startsWith("application/vnd.google-apps")) {
    let exportMimeType;
    switch (file.data.mimeType) {
      case "application/vnd.google-apps.document":
        exportMimeType = "text/markdown";
        break;
      case "application/vnd.google-apps.spreadsheet":
        exportMimeType = "text/csv";
        break;
      case "application/vnd.google-apps.presentation":
        exportMimeType = "text/plain";
        break;
      case "application/vnd.google-apps.drawing":
        exportMimeType = "image/png";
        break;
      default:
        exportMimeType = "text/plain";
    }
    const res = await drive.files.export(
      { fileId, mimeType: exportMimeType },
      { responseType: "text" }
    );
    return {
      contents: [
        {
          uri: request.params.uri,
          mimeType: exportMimeType,
          text: res.data,
        },
      ],
    };
  }
  const res = await drive.files.get(
    { fileId, alt: "media" },
    { responseType: "arraybuffer" }
  );
  const mimeType = file.data.mimeType || "application/octet-stream";
  if (mimeType.startsWith("text/") || mimeType === "application/json") {
    return {
      contents: [
        {
          uri: request.params.uri,
          mimeType: mimeType,
          text: Buffer.from(res.data).toString("utf-8"),
        },
      ],
    };
  } else {
    return {
      contents: [
        {
          uri: request.params.uri,
          mimeType: mimeType,
          blob: Buffer.from(res.data).toString("base64"),
        },
      ],
    };
  }
});

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "search",
        description: "Search for files in Google Drive",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Search query",
            },
          },
          required: ["query"],
        },
      },
      {
        name: "read_file",
        description:
          "Read the contents of a file from Google Drive by its file ID. Exports Google Docs as markdown, Sheets as CSV, Presentations as plain text.",
        inputSchema: {
          type: "object",
          properties: {
            file_id: {
              type: "string",
              description: "The Google Drive file ID",
            },
          },
          required: ["file_id"],
        },
      },
      {
        name: "create_file",
        description:
          "Create a new file in Google Drive. For Google Docs, set mime_type to application/vnd.google-apps.document and provide content as plain text/HTML. For Sheets, use application/vnd.google-apps.spreadsheet.",
        inputSchema: {
          type: "object",
          properties: {
            name: {
              type: "string",
              description: "File name",
            },
            content: {
              type: "string",
              description: "File content (plain text or HTML for Google Docs)",
            },
            mime_type: {
              type: "string",
              description:
                "MIME type. Use application/vnd.google-apps.document for Google Docs, application/vnd.google-apps.spreadsheet for Sheets.",
              default: "application/vnd.google-apps.document",
            },
            parent_id: {
              type: "string",
              description: "Parent folder ID (optional, defaults to root)",
            },
          },
          required: ["name"],
        },
      },
      {
        name: "update_file",
        description:
          "Update the content and/or name of an existing file in Google Drive. For Google Docs, provide new content as plain text/HTML.",
        inputSchema: {
          type: "object",
          properties: {
            file_id: {
              type: "string",
              description: "The Google Drive file ID to update",
            },
            name: {
              type: "string",
              description: "New file name (optional)",
            },
            content: {
              type: "string",
              description: "New file content (optional)",
            },
          },
          required: ["file_id"],
        },
      },
      {
        name: "delete_file",
        description: "Delete a file from Google Drive by its file ID",
        inputSchema: {
          type: "object",
          properties: {
            file_id: {
              type: "string",
              description: "The Google Drive file ID to delete",
            },
          },
          required: ["file_id"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "search") {
    const userQuery = args?.query;
    const escapedQuery = userQuery.replace(/\\/g, "\\\\").replace(/'/g, "\\'");
    const formattedQuery = `fullText contains '${escapedQuery}'`;
    const res = await drive.files.list({
      q: formattedQuery,
      pageSize: 10,
      fields: "files(id, name, mimeType, modifiedTime, size)",
    });
    const fileList = res.data.files
      ?.map((file) => `${file.name} (id: ${file.id}, type: ${file.mimeType})`)
      .join("\n");
    return {
      content: [
        {
          type: "text",
          text: `Found ${res.data.files?.length ?? 0} files:\n${fileList}`,
        },
      ],
    };
  }

  if (name === "read_file") {
    const fileId = args?.file_id;
    const file = await drive.files.get({ fileId, fields: "mimeType, name" });
    if (file.data.mimeType?.startsWith("application/vnd.google-apps")) {
      let exportMimeType;
      switch (file.data.mimeType) {
        case "application/vnd.google-apps.document":
          exportMimeType = "text/markdown";
          break;
        case "application/vnd.google-apps.spreadsheet":
          exportMimeType = "text/csv";
          break;
        case "application/vnd.google-apps.presentation":
          exportMimeType = "text/plain";
          break;
        default:
          exportMimeType = "text/plain";
      }
      const res = await drive.files.export(
        { fileId, mimeType: exportMimeType },
        { responseType: "text" }
      );
      return {
        content: [
          { type: "text", text: `# ${file.data.name}\n\n${res.data}` },
        ],
      };
    }
    const res = await drive.files.get(
      { fileId, alt: "media" },
      { responseType: "arraybuffer" }
    );
    return {
      content: [
        {
          type: "text",
          text: Buffer.from(res.data).toString("utf-8"),
        },
      ],
    };
  }

  if (name === "create_file") {
    const mimeType = args?.mime_type || "application/vnd.google-apps.document";
    const fileMetadata = { name: args?.name, mimeType };
    if (args?.parent_id) {
      fileMetadata.parents = [args.parent_id];
    }

    // For Google-native types, upload content in a format Drive can convert
    const isGoogleNative = mimeType.startsWith(
      "application/vnd.google-apps"
    );
    let uploadMimeType;
    if (mimeType === "application/vnd.google-apps.spreadsheet") {
      uploadMimeType = "text/csv";
    } else if (isGoogleNative) {
      uploadMimeType = "text/html";
    } else {
      uploadMimeType = mimeType;
    }

    const requestBody = { ...fileMetadata };
    // Remove mimeType from requestBody if uploading with media — set it only for conversion
    if (isGoogleNative) {
      // Keep mimeType in requestBody so Drive converts the upload
    }

    const params = {
      requestBody,
      fields: "id, name, mimeType, webViewLink",
    };

    if (args?.content) {
      params.media = {
        mimeType: uploadMimeType,
        body: args.content,
      };
    }

    const res = await drive.files.create(params);
    return {
      content: [
        {
          type: "text",
          text: `Created: ${res.data.name} (id: ${res.data.id})\nType: ${res.data.mimeType}\nLink: ${res.data.webViewLink}`,
        },
      ],
    };
  }

  if (name === "update_file") {
    const fileId = args?.file_id;
    const file = await drive.files.get({ fileId, fields: "mimeType" });
    const params = {
      fileId,
      fields: "id, name, mimeType, webViewLink",
    };
    if (args?.name) {
      params.requestBody = { name: args.name };
    }
    if (args?.content) {
      const isGoogleNative = file.data.mimeType?.startsWith(
        "application/vnd.google-apps"
      );
      params.media = {
        mimeType: isGoogleNative ? "text/html" : file.data.mimeType,
        body: args.content,
      };
    }
    const res = await drive.files.update(params);
    return {
      content: [
        {
          type: "text",
          text: `Updated: ${res.data.name} (id: ${res.data.id})\nLink: ${res.data.webViewLink}`,
        },
      ],
    };
  }

  if (name === "delete_file") {
    const fileId = args?.file_id;
    // Get file name before deleting for confirmation
    const file = await drive.files.get({ fileId, fields: "name" });
    await drive.files.delete({ fileId });
    return {
      content: [
        {
          type: "text",
          text: `Deleted: ${file.data.name} (id: ${fileId})`,
        },
      ],
    };
  }

  throw new Error(`Tool not found: ${name}`);
});

const credentialsPath =
  process.env.GDRIVE_CREDENTIALS_PATH ||
  path.join(
    path.dirname(new URL(import.meta.url).pathname),
    "../../../.gdrive-server-credentials.json"
  );

const oauthKeysPath =
  process.env.GDRIVE_OAUTH_PATH ||
  path.join(
    path.dirname(new URL(import.meta.url).pathname),
    "../../../gcp-oauth.keys.json"
  );

function loadOAuthKeys() {
  const keysContent = JSON.parse(fs.readFileSync(oauthKeysPath, "utf-8"));
  const keys = keysContent.installed || keysContent.web;
  if (!keys) {
    throw new Error(
      "OAuth keys file must contain 'installed' or 'web' credentials"
    );
  }
  return keys;
}

async function authenticateAndSaveCredentials() {
  console.log("Launching auth flow…");
  const auth = await authenticate({
    keyfilePath: oauthKeysPath,
    scopes: ["https://www.googleapis.com/auth/drive"],
  });
  fs.writeFileSync(credentialsPath, JSON.stringify(auth.credentials));
  console.log("Credentials saved. You can now run the server.");
}

async function loadCredentialsAndRunServer() {
  if (!fs.existsSync(credentialsPath)) {
    console.error(
      "Credentials not found. Please run with 'auth' argument first."
    );
    process.exit(1);
  }
  const credentials = JSON.parse(fs.readFileSync(credentialsPath, "utf-8"));

  // Load client ID/secret so the OAuth2 client can auto-refresh tokens
  const keys = loadOAuthKeys();
  const auth = new google.auth.OAuth2(
    keys.client_id,
    keys.client_secret,
    keys.redirect_uris?.[0]
  );
  auth.setCredentials(credentials);

  // Persist refreshed tokens so they survive server restarts
  auth.on("tokens", (newTokens) => {
    const merged = { ...credentials, ...newTokens };
    fs.writeFileSync(credentialsPath, JSON.stringify(merged));
    console.error("Token refreshed and saved.");
  });

  google.options({ auth });
  console.error("Credentials loaded. Starting server.");
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

if (process.argv[2] === "auth") {
  authenticateAndSaveCredentials().catch(console.error);
} else {
  loadCredentialsAndRunServer().catch(console.error);
}
