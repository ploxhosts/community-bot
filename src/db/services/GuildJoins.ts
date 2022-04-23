import sequelize from "../database";
import { DataTypes, Model } from 'sequelize';

class GuildJoins extends Model {
    declare id: number;
    declare user_id: string;
    declare invite_link: string;
    declare left_at: string;
    declare last_message_id: string;
}

GuildJoins.init({
    id: {
        type: DataTypes.INTEGER,
        autoIncrement: true,
        primaryKey: true
    },
    user_id: {
        type: DataTypes.STRING,
        allowNull: false
    },
    invite_link: {
        type: DataTypes.STRING,
        allowNull: false
    },
    left_at: {
        type: DataTypes.STRING,
        allowNull: true
    },
    last_message_id: {
        type: DataTypes.STRING,
        allowNull: true
    }
}, {
  sequelize,
  modelName: 'GuildJoins'
});
