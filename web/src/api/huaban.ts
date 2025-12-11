
export interface HuabanCollection {
    collection_id: number;
    user_id: number;
    title: string;
    description: string;
    board_ids: string;
    seq: number;
    created_at: number;
    extra: any;
}

export interface HuabanCollectionsResponse {
    collections: HuabanCollection[];
}

export const getHuabanCollections = async (): Promise<any> => {
    const response = await fetch('/huaban-api/v3/users/30904678/collections', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        }
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch collections: ${response.status} ${response.statusText}`);
    }

    return response.json();
}

export interface HuabanPin {
    pin_id: number;
    file: {
        key: string;
        type: string;
        width: number;
        height: number;
        url?: string;
    };
    raw_text: string;
}

export interface HuabanBoard {
    board_id: number;
    title: string;
    updated_at: number;
    pin_count: number;
    pins?: HuabanPin[];
    cover: {
        file: {
            key: string;
            url?: string;
        }
    };
}

export interface HuabanCollectionItemsResponse {
    pins: HuabanPin[];
    user: {
        boards: HuabanBoard[];
    };
}

export const getHuabanCollectionItems = async (collectionId: number): Promise<HuabanCollectionItemsResponse> => {
    const response = await fetch(`/huaban-api/v3/ltnwxonyzk/collections/${collectionId}?limit=50`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        }
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch collection items: ${response.status} ${response.statusText}`);
    }

    return response.json();
}

export interface HuabanBoardDetailResponse {
    pins: HuabanPin[];
    board: HuabanBoard;
}

export const getHuabanBoardDetail = async (boardId: number, max?: number): Promise<HuabanBoardDetailResponse> => {
    const fields = encodeURIComponent('pins:PIN|board:BOARD_DETAIL|check');
    let url = `/huaban-api/v3/boards/${boardId}/pins?limit=40&sort=seq&fields=${fields}`;
    if (max) {
        url += `&max=${max}`;
    }

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        }
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch board details: ${response.status} ${response.statusText}`);
    }

    return response.json();
}
