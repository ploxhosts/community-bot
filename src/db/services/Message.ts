import sequelize from "../database";
import { DataTypes, Model } from 'sequelize';

class Message extends Model {
    declare id: number;
    declare user_id: string;
    declare channel_id: string;
    declare message: string;
    declare embed: string;
    declare in_thread: boolean;
    declare thread_id: string;
    declare in_response_to: string;
    declare response_to: string;
    declare is_pinned: boolean;
    declare is_deleted: boolean;
    declare is_edited: boolean;
    declare reported: boolean;
    declare reactions: string[];
    declare attachments: string[];
    declare message_id_before: string;
    declare edits: string[];
}

Message.init({
    id: {
        type: DataTypes.STRING,
        primaryKey: true
    },
    user_id: {
        type: DataTypes.STRING,
        allowNull: false
    },
    channel_id: {
        type: DataTypes.STRING,
        allowNull: false
    },
    message: {
        type: DataTypes.STRING,
        allowNull: false
    },
    embed: {
        type: DataTypes.STRING,
        allowNull: true
    },
    in_thread: {
        type: DataTypes.BOOLEAN,
        allowNull: false
    },
    in_response_to: {
        type: DataTypes.STRING,
        allowNull: true
    },
    is_pinned: {
        type: DataTypes.BOOLEAN,
        allowNull: false
    },
    is_deleted: {
        type: DataTypes.BOOLEAN,
        allowNull: false
    },
    is_edited: {
        type: DataTypes.BOOLEAN,
        allowNull: false
    },
    reported: {
        type: DataTypes.BOOLEAN,
        allowNull: false
    },
    reactions: {
        type: DataTypes.ARRAY(DataTypes.STRING),
        allowNull: true
    },
    attachments: {
        type: DataTypes.ARRAY(DataTypes.STRING),
        allowNull: true
    },
    message_id_before: {
        type: DataTypes.STRING,
        allowNull: true
    },
    edits: {
        type: DataTypes.ARRAY(DataTypes.STRING),
        allowNull: true
    },

}, {
  sequelize,
  modelName: 'Message'
});
