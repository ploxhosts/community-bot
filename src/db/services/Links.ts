import sequelize from "../database";
import { DataTypes, Model } from 'sequelize';

class Link extends Model {
    declare id: number;
    declare hostname: string;
    declare link: string;
    declare added_by: string;
    declare allowed: boolean;
    declare score: number;
    declare process: string[];
}

Link.init({
    id: {
        type: DataTypes.INTEGER,
        autoIncrement: true,
        primaryKey: true
    },
    hostname: {
        type: DataTypes.STRING,
        allowNull: false
    },
    link: {
        type: DataTypes.STRING,
        allowNull: false
    },
    added_by: {
        type: DataTypes.STRING,
        allowNull: false
    },
    allowed: {
        type: DataTypes.BOOLEAN,
        allowNull: false
    },
    score: {
        type: DataTypes.INTEGER,
        allowNull: false
    },
    process: {
        type: DataTypes.ARRAY(DataTypes.STRING),
        allowNull: false
    }
}, {
  sequelize,
  modelName: 'Link'
});
