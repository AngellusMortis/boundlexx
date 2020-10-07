// Optional: You can use `msgpack` instead of JSON for some serious download size gains
// See https://gist.github.com/AngellusMortis/a6dec43a8614ac5ff5dc47b38da68750
// For how to automatically set it up with Axios

const mapMsgpack = (root: any, key_map: string[]) => {
    const mappedData: any = root instanceof Array ? [] : {};

    Reflect.ownKeys(root).forEach((index) => {
        let value = root[index];
        let finalKey: string | number;

        if (typeof index == "symbol") {
            return;
        } else if (typeof index == "string") {
            finalKey = parseInt(index);
        } else {
            finalKey = index;
        }

        if (value !== null && (value instanceof Array || typeof value == "object")) {
            value = mapMsgpack(value, key_map);
        }

        if (key_map[finalKey] !== undefined && !Array.isArray(root)) {
            finalKey = key_map[finalKey];
        }
        mappedData[finalKey] = value;
    });
    return mappedData;
};


const axiosConfig = {
    params: {
        format: "msgpack",
    },
    responseType: "arraybuffer",
    transformResponse: [
        (data: ArrayBuffer): any => {
            const unmappedData = msgpack.decode(new Uint8Array(data));
            mapMsgpack(unmappedData[0], unmappedData[1]);
        },
    ],
};
