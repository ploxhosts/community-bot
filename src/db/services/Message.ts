import sequelize from "../database";
import { DataTypes, Model } from 'sequelize';

class Message extends Model {
    declare id: number;
    declare username: string;
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
