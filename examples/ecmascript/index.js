// https://github.com/anttiviljami/openapi-client-axios
// OpenAPI Client generator for Axios
const OpenAPIClientAxios = require('openapi-client-axios').default;
// https://github.com/mpyw/axios-case-converter
// Optional
// Converts Python backends snake case to standard ECMAScript camelCase
const applyCaseMiddleware = require('axios-case-converter').default;

async function main() {
    const api = new OpenAPIClientAxios({ definition: 'https://api.boundlexx.app/api/v1/schema/?format=openapi-json' });
    // or Testing Universe
    api.withServer("Live Universe");

    const client = applyCaseMiddleware(await api.getClient());

    // list worlds with filters
    let res = await client.listWorlds([{ "name": "limit", value: 1, in: "query" }]);
    console.log(res.data);
    // {
    //     count: 1043,
    //     next: 'https://api.boundlexx.app/api/v1/worlds/?limit=1&offset=1',
    //     previous: null,
    //     results: [
    //       {
    //         url: 'https://api.boundlexx.app/api/v1/worlds/1/',
    //         pollsUrl: 'https://api.boundlexx.app/api/v1/worlds/1/polls/',
    //         blockColorsUrl: 'https://api.boundlexx.app/api/v1/worlds/1/block-colors/',
    //         distancesUrl: 'https://api.boundlexx.app/api/v1/worlds/1/distances/',
    //         requestBasketsUrl: 'https://api.boundlexx.app/api/v1/worlds/1/request-baskets/',
    //         nextRequestBasketUpdate: null,
    //         shopStandsUrl: 'https://api.boundlexx.app/api/v1/worlds/id/shop-stands/',
    //         nextShopStandUpdate: null,
    //         id: 1,
    //         active: true,
    //         name: 'euc1_t0_0',
    //         displayName: 'Sochaltin I',
    //         textName: 'Sochaltin I',
    //         htmlName: 'Sochaltin I',
    //         address: 'gs-live-euc1.playboundless.com',
    //         imageUrl: 'https://cdn.boundlexx.app/worlds/sochaltin_i.png',
    //         forumUrl: 'https://forum.playboundless.com/t/42624',
    //         assignment: null,
    //         region: 'euc',
    //         tier: 0,
    //         size: 288,
    //         worldType: 'LUSH',
    //         specialType: 0,
    //         protectionPoints: null,
    //         protectionSkill: null,
    //         timeOffset: '2018-08-16T11:52:28.706624-04:00',
    //         isSovereign: false,
    //         isPerm: true,
    //         isExo: false,
    //         isCreative: false,
    //         isLocked: false,
    //         isPublic: true,
    //         isPublicEdit: null,
    //         isPublicClaim: null,
    //         isFinalized: null,
    //         numberOfRegions: 50,
    //         start: '2018-08-15T20:00:00-04:00',
    //         end: null,
    //         atmosphereColor: '#53f8ff',
    //         waterColor: '#4e9797',
    //         surfaceLiquid: 'Water',
    //         coreLiquid: 'Water',
    //         bows: null
    //         }
    //     ]
    // }

    // get world
    res = await client.retrieveWorld(10);
    console.log(res.data);
    // {
    //     url: 'https://api.boundlexx.app/api/v1/worlds/10/',
    //     pollsUrl: 'https://api.boundlexx.app/api/v1/worlds/10/polls/',
    //     blockColorsUrl: 'https://api.boundlexx.app/api/v1/worlds/10/block-colors/',
    //     distancesUrl: 'https://api.boundlexx.app/api/v1/worlds/10/distances/',
    //     requestBasketsUrl: 'https://api.boundlexx.app/api/v1/worlds/10/request-baskets/',
    //     nextRequestBasketUpdate: null,
    //     shopStandsUrl: 'https://api.boundlexx.app/api/v1/worlds/id/shop-stands/',
    //     nextShopStandUpdate: null,
    //     id: 10,
    //     active: true,
    //     name: 'use1_t4_0',
    //     displayName: 'Serpensarindi',
    //     textName: 'Serpensarindi',
    //     htmlName: 'Serpensarindi',
    //     address: 'gs-live-use1.playboundless.com',
    //     imageUrl: 'https://cdn.boundlexx.app/worlds/serpensarindi.png',
    //     forumUrl: 'https://forum.playboundless.com/t/42645',
    //     assignment: null,
    //     region: 'use',
    //     tier: 4,
    //     size: 288,
    //     worldType: 'BLAST',
    //     specialType: 0,
    //     protectionPoints: 3,
    //     protectionSkill: {
    //       url: 'https://api.boundlexx.app/api/v1/skills/73/',
    //       name: 'Volatile Atmosphere Armour'
    //     },
    //     timeOffset: '2018-08-16T12:47:00.003152-04:00',
    //     isSovereign: false,
    //     isPerm: true,
    //     isExo: false,
    //     isCreative: false,
    //     isLocked: false,
    //     isPublic: true,
    //     isPublicEdit: null,
    //     isPublicClaim: null,
    //     isFinalized: null,
    //     numberOfRegions: 50,
    //     start: '2018-08-15T20:00:00-04:00',
    //     end: null,
    //     atmosphereColor: '#f3f3f3',
    //     waterColor: '#909090',
    //     surfaceLiquid: 'Water',
    //     coreLiquid: 'Lava',
    //     bows: {
    //       best: [ 'emerald' ],
    //       neutral: [ 'amethyst', 'sapphire' ],
    //       lucent: [ 'umbris' ]
    //     }
    // }
}

main();
