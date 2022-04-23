import sequelize from "../database";
import { DataTypes, Model } from 'sequelize';

class User extends Model {
    declare id: number;
    declare username: string;
    declare discriminator: string;
    declare avatar: string;
    declare premium: number;
    declare banned: boolean;
    declare timedOut: boolean;
    declare lastSeen: Date;
    declare roles: string[];
    declare email: string;
    declare verified: boolean;
    declare ip: string;
    declare nickname: string;
}

User.init({
    id: {
        type: DataTypes.STRING,
        primaryKey: true
    },
    username: {
        type: DataTypes.STRING,
        allowNull: false
    },
    discriminator: {
        type: DataTypes.STRING,
        allowNull: false
    },
    avatar: {
        type: DataTypes.STRING,
        allowNull: false
    },
    premium: {
        type: DataTypes.INTEGER,
        defaultValue: 0,
        allowNull: false
    },
    banned: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,
        allowNull: false
    },
    timedOut: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,
        allowNull: false
    },
    lastSeen: {
        type: DataTypes.DATE,
        allowNull: true
    },
    roles: {
        type: DataTypes.ARRAY(DataTypes.STRING),
        allowNull: true
    },
    email: {
        type: DataTypes.STRING,
        allowNull: true
    },
    verified: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,
        allowNull: false
    },
    ip: {
        type: DataTypes.STRING,
        allowNull: true
    },
    nickname: {
        type: DataTypes.STRING,
        allowNull: true
    }

}, {
  sequelize,
  modelName: 'User'
});
