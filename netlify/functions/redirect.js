export async function handler(event, context) {
    const params = event.queryStringParameters || {};
    const pkg = params.package;
    const tag = params.tag || "1.0";

    if (!pkg || !pkg.endsWith(".deb")) {
        return {
            statusCode: 400,
            body: "Invalid or missing package parameter",
        };
    }

    // Build GitHub release URL
    const target = `https://github.com/denova234/novaide-packages/releases/download/${tag}/${pkg}`;

    // Return HTTP 302 redirect
    return {
        statusCode: 302,
        headers: {
            Location: target,
        },
    };
}